from cors_config import init_cors
from security import init_security
from models import *
from functools import wraps
from collections import defaultdict
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import DishForm, ReviewForm, RegisterForm
from db import *
from sockets import socketio, emit_order_status_update
import os
import uuid
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from logging_config import setup_logging, init_sentry

load_dotenv()

app = Flask(__name__)

# Database configuration (use DATABASE_URL if provided, otherwise fallback to sqlite)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

# Initialize security features
init_security(app)

# Initialize CORS (applies secure CORS config depending on environment)
init_cors(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models after initializing SQLAlchemy

# Set up logging
setup_logging(app)

# Initialize Sentry for production error tracking
init_sentry(app)
# Replace with a real secret key in your environment variables
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['ADMIN_CLAIM_CODE'] = os.environ.get(
    'ADMIN_CLAIM_CODE', '@hmed@zimi04')
# Initialize CSRF protection
csrf = CSRFProtect(app)
# Initialize Supabase clients
supabase_url = os.environ.get('SUPABASE_URL')
supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_service_role_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if supabase_url and supabase_anon_key:
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    supabase_admin: Client = create_client(
        supabase_url, supabase_service_role_key)
else:
    # Supabase is optional when using own Postgres (Docker). Log and continue.
    supabase = None
    supabase_admin = None
    app.logger.info(
        'Supabase not configured; proceeding without Supabase clients')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio.init_app(app, async_mode='eventlet')


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        # Create a user object for Flask-Login
        class User(UserMixin):
            def __init__(self, data):
                self.id = data['id']
                self.username = data['username']
                self.email = data['email']
                self.is_admin = data['is_admin']
                self.points = data['points']

            def get_id(self):
                return str(self.id)

        return User(user_data)
    return None


# Admin check decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Admin access required!')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# --- Admin Routes ---


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    dishes = get_all_dishes()
    return render_template('admin_dashboard.html', dishes=dishes)

# Add dish


@app.route('/admin/dish/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_dish():
    form = DishForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join('static', 'uploads', filename)
            try:
                image_file.save(upload_path)
                image_filename = filename
            except Exception as e:
                print(f"Error saving image: {e}")
                flash('Error saving image!')
                return render_template('admin_add_dish.html', form=form)

        dish = create_dish(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            image_filename=image_filename,
            section=form.section.data
        )
        if dish:

            flash('Dish added!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Error adding dish!')
    return render_template('admin_add_dish.html', form=form)

# Edit dish


@app.route('/admin/dish/edit/<dish_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_dish(dish_id):
    dish = get_dish_by_id(dish_id)
    if not dish:
        flash('Dish not found!')
        return redirect(url_for('admin_dashboard'))

    form = DishForm(obj=dish)
    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'price': form.price.data,
            'description': form.description.data,
            'section': form.section.data
        }

        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join('static', 'uploads', filename)
            image_file.save(upload_path)
            updates['image_filename'] = filename

        if update_dish(dish_id, updates):
            flash('Dish updated!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Error updating dish!')
    return render_template('admin_edit_dish.html', form=form, dish=dish)

# Delete dish


@app.route('/admin/dish/delete/<dish_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_dish(dish_id):
    if delete_dish(dish_id):
        flash('Dish deleted!')
    else:
        flash('Error deleting dish!')
    return redirect(url_for('admin_dashboard'))

# Admin orders route


@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    orders = get_all_orders()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/orders/<order_id>/status/<status>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id, status):
    if status not in ['pending', 'preparing', 'ready', 'delivered']:
        flash('Invalid status')
        return redirect(url_for('admin_orders'))

    if update_order_status(order_id, status):
        flash(f'Order {order_id} status updated to {status}')
        try:
            emit_order_status_update(socketio, order_id, status)
        except Exception as e:
            print(f"SocketIO emit failed: {e}")
    else:
        flash('Error updating order status')
    return redirect(url_for('admin_orders'))


@app.route('/admin/revenue')
@login_required
@admin_required
def admin_revenue():
    from db import get_total_revenue, get_revenue_by_dish, get_daily_revenue, get_monthly_revenue

    total_revenue = get_total_revenue()
    dish_revenue = get_revenue_by_dish()
    daily_revenue = get_daily_revenue(30)
    monthly_revenue = get_monthly_revenue(12)

    return render_template('admin_revenue.html',
                           total_revenue=total_revenue,
                           dish_revenue=dish_revenue,
                           daily_revenue=daily_revenue,
                           monthly_revenue=monthly_revenue)


@app.route('/admin/promote_all', methods=['POST'])
@login_required
@admin_required
def promote_all_users():
    admin_code = request.form.get('admin_code', '').strip()
    admin_code = ''.join(admin_code.split())  # Remove all spaces
    if admin_code.lower() == app.config.get('ADMIN_CLAIM_CODE').lower():
        users = get_all_users()
        for user in users:
            update_user(user['id'], {'is_admin': True})
        flash('All users have been promoted to admin.')
    else:
        flash('Invalid admin code.')
    return redirect(url_for('admin_dashboard'))

# --- Main Routes ---


@app.route('/')
def home():
    dishes = get_all_dishes()
    # Group dishes by section
    sections = defaultdict(list)
    for dish in dishes:
        sections[dish['section']].append(dish)
    return render_template('home.html', sections=sections)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        admin_code = form.admin_code.data.strip() if form.admin_code.data else ''
        admin_code = ''.join(admin_code.split())  # Remove all spaces

        # Check if user exists in Supabase Auth
        try:
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            if auth_response.user:
                auth_user_id = auth_response.user.id
                is_admin = admin_code.lower() == app.config.get('ADMIN_CLAIM_CODE').lower()
                user = create_user(auth_user_id, username, email, is_admin)
                if user:
                    if is_admin:
                        flash(
                            'Registration successful! You have been registered as an admin. Please log in.')
                    else:
                        flash('Registration successful! Please log in.')
                    return redirect(url_for('login'))
                else:
                    flash(
                        'Account creation failed. Please contact support if this persists.')
            else:
                flash('Authentication registration failed. Please try again.')
        except Exception as e:
            print(f"Supabase auth error: {e}")
            error_msg = str(e).lower()
            if "password" in error_msg and ("weak" in error_msg or "short" in error_msg):
                flash(
                    'Password is too weak. Please choose a stronger password (at least 6 characters).')
            elif "email" in error_msg and ("invalid" in error_msg or "format" in error_msg):
                flash('Invalid email format. Please enter a valid email address.')
            elif "already registered" in error_msg or "already exists" in error_msg:
                flash('Email already registered. Please try logging in instead.')
            elif "network" in error_msg or "connection" in error_msg:
                flash('Network error. Please check your connection and try again.')
            else:
                flash('Registration failed due to an error. Please try again.')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if auth_response.user:
                user_data = get_user_by_auth_id(auth_response.user.id)
                if user_data:
                    # Create user object for Flask-Login
                    class User(UserMixin):
                        def __init__(self, data):
                            self.id = data['id']
                            self.username = data['username']
                            self.email = data['email']
                            self.is_admin = data['is_admin']
                            self.points = data['points']

                        def get_id(self):
                            return str(self.id)

                    user = User(user_data)
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    flash('User not found in database. Please register first.')
            else:
                flash('Invalid credentials')
        except Exception as e:
            print(f"Supabase auth error: {e}")
            flash('Login failed. Please check your credentials.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    # Fetch all dishes
    dishes = get_all_dishes()

    # Get review stats for all dishes
    review_stats = get_review_stats()

    menu_sections = defaultdict(list)
    for dish in dishes:
        stats = review_stats.get(
            dish['id'], {'avg_rating': 0, 'review_count': 0})
        dish['avg_rating'] = stats['avg_rating']
        dish['review_count'] = stats['review_count']
        menu_sections[dish['section']].append(dish)

    # Define the desired order of sections
    section_order = ['Breakfast', 'Lunch', 'Dinner',
                     'Drinks', 'Daily Specials', 'Other']
    sorted_menu_sections = {key: menu_sections[key]
                            for key in section_order if key in menu_sections}
    return render_template('menu.html', menu_sections=sorted_menu_sections)


@app.route('/add_to_cart/<dish_id>', methods=['POST'])
@login_required
def add_to_cart(dish_id):
    try:
        dish = get_dish_by_id(dish_id)
        if not dish:
            flash('Dish not found!')
            return redirect(url_for('menu'))

        if add_to_cart(current_user.id, dish_id):
            flash('Added to cart!')
        else:
            flash('Error adding to cart!')
        return redirect(url_for('menu'))
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        flash('Error adding to cart!')
        return redirect(url_for('menu'))


@app.route('/dish/<dish_id>', methods=['GET'])
@login_required
def dish_detail(dish_id):
    try:
        dish = get_dish_by_id(dish_id)
        if not dish:
            flash('Dish not found!')
            return redirect(url_for('menu'))

        form = ReviewForm()
        reviews = get_reviews_by_dish(dish_id)
        # Calculate average rating and review count
        stats = calculate_review_stats(reviews)
        dish['avg_rating'] = stats['avg_rating']
        dish['review_count'] = stats['review_count']
        return render_template('dish_detail.html', dish=dish, review_form=form, reviews=reviews)
    except Exception as e:
        print(f"Error in dish_detail: {e}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while loading the dish details.')
        return redirect(url_for('menu'))


@app.route('/dish/<dish_id>/review', methods=['POST'])
@login_required
def submit_review(dish_id):
    try:
        dish = get_dish_by_id(dish_id)
        if not dish:
            flash('Dish not found!')
            return redirect(url_for('menu'))

        form = ReviewForm()
        reviews = get_reviews_by_dish(dish_id)
        if form.validate_on_submit():
            rating = form.rating.data
            if create_review(current_user.id, dish_id, int(rating) if rating else None, form.review_text.data):
                flash('Review submitted!')
                return redirect(url_for('dish_detail', dish_id=dish_id))
            else:
                flash('Error submitting review.')
        else:
            flash('Please select a rating.')

        # Calculate average rating and review count for the template
        stats = calculate_review_stats(reviews)
        dish['avg_rating'] = stats['avg_rating']
        dish['review_count'] = stats['review_count']
        return render_template('dish_detail.html', dish=dish, review_form=form, reviews=reviews)
    except Exception as e:
        print(f"Error in submit_review: {e}")
        flash('An error occurred while submitting the review.')
        return redirect(url_for('dish_detail', dish_id=dish_id))


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    cart_items = get_cart_items(current_user.id)
    items = []
    total = 0
    for item in cart_items:
        dish = item['dish']
        if dish:
            subtotal = dish['price'] * item['quantity']
            total += subtotal
            items.append({
                'dish': dish,
                'quantity': item['quantity'],
                'subtotal': subtotal,
                'cart_item_id': item['id']
            })

    discount = 0
    if request.method == 'POST' and 'use_points' in request.form:
        points_to_use = min(current_user.points, int(
            total * 10))  # Max 10% discount
        session['redeem_points'] = points_to_use
        discount = points_to_use / 10  # $1 per 10 points
    elif 'redeem_points' in session:
        points_to_use = min(session['redeem_points'], int(
            total * 10))  # Max 10% discount
        discount = points_to_use / 10  # $1 per 10 points

    return render_template('cart.html', items=items, total=total, discount=discount, user=current_user)


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        cart_items = get_cart_items(current_user.id)
        if not cart_items:
            flash('Your cart is empty!')
            return redirect(url_for('cart'))
        total = 0
        order = create_order(current_user.id, 0, None)
        if not order:
            flash('Error creating order!')
            return redirect(url_for('cart'))

        for item in cart_items:
            dish = item['dish']
            if dish:
                subtotal = dish['price'] * item['quantity']
                total += subtotal
                create_order_item(order['id'], dish['id'],
                                  item['quantity'], dish['price'])
                remove_cart_item(item['id'])

        discount = float(request.form.get('discount', 0))
        final_total = total - discount
        points_earned = int(final_total)  # 1 point per $1 spent

        # Update order with final total and points
        # This is just to update, but we need to add total update
        update_order_status(order['id'], 'pending')
        # Note: We need to add a function to update order total and points

        # Update user points
        current_user.points += points_earned
        update_user(current_user.id, {'points': current_user.points})

        if 'redeem_points' in session:
            # Clear redeemed points after checkout
            session.pop('redeem_points')

        # For now, manually update order total (we should add this to db.py)
        # This is a temporary fix - ideally we'd have update_order function
        try:
            supabase.table('order').update(
                {'total': final_total, 'points_earned': points_earned}).eq('id', order['id']).execute()
        except Exception as e:
            print(f"Error updating order total: {e}")

        return render_template('order_confirmation.html', order=order, discount=discount)
    except Exception as e:
        print(f"Error in checkout: {e}")
        flash('An error occurred during checkout.')
        return redirect(url_for('cart'))


@app.route('/cart/update/<cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    try:
        quantity = int(request.form['quantity'])
        if update_cart_item(cart_item_id, quantity):
            flash('Cart updated!')
        else:
            flash('Error updating cart!')
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error in update_cart_item: {e}")
        flash('Error updating cart!')
        return redirect(url_for('cart'))


@app.route('/cart/remove/<cart_item_id>', methods=['POST'])
@login_required
def remove_cart_item(cart_item_id):
    try:
        if remove_cart_item(cart_item_id):
            flash('Item removed from cart!')
        else:
            flash('Error removing item from cart!')
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error in remove_cart_item: {e}")
        flash('Error removing item from cart!')
        return redirect(url_for('cart'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form.get('password')

        # Check for unique username/email (ignore current user's own)
        all_users = get_all_users()
        existing_username = any(
            u['username'] == username and u['id'] != current_user.id for u in all_users)
        existing_email = any(u['email'] == email and u['id']
                             != current_user.id for u in all_users)

        if existing_username:
            flash('Username already taken')
        elif existing_email:
            flash('Email already taken')
        else:
            updates = {'username': username, 'email': email}
            if update_user(current_user.id, updates):
                # Update current_user object
                current_user.username = username
                current_user.email = email

                if password:
                    # Update password in Supabase Auth
                    try:
                        supabase.auth.update_user({"password": password})
                        flash('Profile updated!')
                    except Exception as e:
                        print(f"Supabase password update error: {e}")
                        flash('Profile updated but password change failed.')
                else:
                    flash('Profile updated!')
            else:
                flash('Error updating profile!')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user)


@app.route('/claim_admin', methods=['GET', 'POST'])
@login_required
def claim_admin():
    if request.method == 'POST':
        code = request.form.get('admin_code', '')
        if code == app.config.get('ADMIN_CLAIM_CODE'):
            if update_user(current_user.id, {'is_admin': True}):
                current_user.is_admin = True
                flash('You have been granted admin privileges.')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Error granting admin privileges.')
        else:
            flash('Invalid admin code.')
            return redirect(url_for('claim_admin'))
    return render_template('claim_admin.html')

# --- CLI Commands ---


def seed_database():
    # Check if dishes already exist
    existing_dishes = get_all_dishes()
    if existing_dishes:
        print('Dishes already exist. Skipping seeding.')
        return

    dishes = [
        # Breakfast
        {"section": "Breakfast", "name": "Classic Breakfast", "price": 9.99,
            "description": "Eggs, toast, and more.", "image_filename": None},
        {"section": "Breakfast", "name": "Pancake Stack", "price": 7.99,
            "description": "Fluffy pancakes with syrup.", "image_filename": None},
        {"section": "Breakfast", "name": "Avocado Toast", "price": 8.50,
            "description": "Sourdough with smashed avocado.", "image_filename": None},
        {"section": "Breakfast", "name": "Oatmeal Bowl", "price": 6.50,
            "description": "Healthy oatmeal with fruit.", "image_filename": None},
        # Lunch
        {"section": "Lunch", "name": "Chicken Sandwich", "price": 12.50,
            "description": "Grilled chicken sandwich.", "image_filename": None},
        {"section": "Lunch", "name": "Burger Deluxe", "price": 14.75,
            "description": "Juicy beef burger.", "image_filename": None},
        {"section": "Lunch", "name": "Caesar Salad", "price": 10.00,
            "description": "Classic Caesar salad.", "image_filename": None},
        {"section": "Lunch", "name": "Veggie Wrap", "price": 11.50,
            "description": "Fresh veggie wrap.", "image_filename": None},
        # Dinner
        {"section": "Dinner", "name": "Spaghetti & Meatballs", "price": 16.99,
            "description": "Classic spaghetti with meatballs.", "image_filename": None},
        {"section": "Dinner", "name": "Grilled Salmon", "price": 18.50,
            "description": "Grilled salmon fillet.", "image_filename": None},
        {"section": "Dinner", "name": "Ribeye Steak", "price": 25.00,
            "description": "Juicy ribeye steak.", "image_filename": None},
        {"section": "Dinner", "name": "Chicken Parmesan", "price": 17.50,
            "description": "Breaded chicken with cheese.", "image_filename": None}
    ]

    for dish_data in dishes:
        create_dish(**dish_data)
    print('Seeded dishes!')


@app.cli.command('seed')
def seed():
    seed_database()


# Make the first user an admin (run once)
@app.cli.command('make_admin')
def make_admin():
    users = get_all_users()
    if users:
        user = users[0]
        update_user(user['id'], {'is_admin': True})
        print(f'User {user["username"]} is now an admin.')

    # Initialize rate limiting
    from rate_limiting import init_limiter, configure_route_limits
    limiter = init_limiter(app)

    # Configure rate limits for routes after all routes are defined
    configure_route_limits(app, limiter)
# Error handlers


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {request.url}')
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    app.logger.error(f'Forbidden access: {request.url}')
    return render_template('errors/403.html'), 403


@app.errorhandler(Exception)
def unhandled_exception(error):
    app.logger.error(f'Unhandled Exception: {error}')
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
