from functools import wraps
from collections import defaultdict
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_socketio import SocketIO
from forms import DishForm, ReviewForm
from models import db, User, Dish, Order, OrderItem, CartItem, Review
from sockets import socketio, emit_order_status_update
import os

app = Flask(__name__)
# Replace with a real secret key in your environment variables
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'a-secure-random-string-that-you-should-replace')
app.config['ADMIN_CLAIM_CODE'] = os.environ.get(
    'ADMIN_CLAIM_CODE', '@hmed@zimi04')
# Use Heroku's DATABASE_URL if available, otherwise fall back to local SQLite
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath("instance/stitch_menu.db")}'
else:
    database_url = database_url.replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio.init_app(app, async_mode='eventlet')

# Create tables and seed if not exist
with app.app_context():
    db.create_all()
    # seed_database()  # Commented out to avoid seeding on every run


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    dishes = Dish.query.all()
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
        dish = Dish(name=form.name.data, price=form.price.data, description=form.description.data,
                    image_filename=image_filename, section=form.section.data)
        db.session.add(dish)
        try:
            db.session.commit()
            flash('Dish added!')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            print(f"Error committing dish: {e}")
            db.session.rollback()
            flash('Error adding dish!')
    return render_template('admin_add_dish.html', form=form)

# Edit dish


@app.route('/admin/dish/edit/<int:dish_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    form = DishForm(obj=dish)
    if form.validate_on_submit():
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join('static', 'uploads', filename)
            image_file.save(upload_path)
            dish.image_filename = filename
        form.populate_obj(dish)
        db.session.commit()
        flash('Dish updated!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_dish.html', form=form, dish=dish)

# Delete dish


@app.route('/admin/dish/delete/<int:dish_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    db.session.delete(dish)
    db.session.commit()
    flash('Dish deleted!')
    return redirect(url_for('admin_dashboard'))

# Admin orders route


@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/orders/<int:order_id>/status/<status>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id, status):
    if status not in ['pending', 'preparing', 'ready', 'delivered']:
        flash('Invalid status')
        return redirect(url_for('admin_orders'))
    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()
    flash(f'Order {order_id} status updated to {status}')
    try:
        emit_order_status_update(socketio, order_id, status)
    except Exception as e:
        print(f"SocketIO emit failed: {e}")
    return redirect(url_for('admin_orders'))


@app.route('/admin/promote_all', methods=['POST'])
@login_required
@admin_required
def promote_all_users():
    admin_code = request.form.get('admin_code', '').strip()
    admin_code = ''.join(admin_code.split())  # Remove all spaces
    if admin_code.lower() == app.config.get('ADMIN_CLAIM_CODE').lower():
        users = User.query.all()
        for user in users:
            user.is_admin = True
        db.session.commit()
        flash('All users have been promoted to admin.')
    else:
        flash('Invalid admin code.')
    return redirect(url_for('admin_dashboard'))

# --- Main Routes ---


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        admin_code = request.form.get('admin_code', '').strip()
        admin_code = ''.join(admin_code.split())  # Remove all spaces
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        is_admin = admin_code.lower() == app.config.get('ADMIN_CLAIM_CODE').lower()
        user = User(username=username, email=email,
                    password=hashed_password, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        if is_admin:
            flash(
                'Registration successful! You have been registered as an admin. Please log in.')
        else:
            flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    from sqlalchemy import func

    # Fetch all dishes
    dishes = Dish.query.all()

    # Calculate average rating and review count for all dishes in one query
    review_stats = db.session.query(
        Review.dish_id,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).filter(Review.rating.isnot(None)).group_by(Review.dish_id).all()

    # Create a dict for quick lookup
    stats_dict = {stat.dish_id: {'avg_rating': stat.avg_rating or 0,
                                 'review_count': stat.review_count} for stat in review_stats}

    menu_sections = defaultdict(list)
    for dish in dishes:
        stats = stats_dict.get(dish.id, {'avg_rating': 0, 'review_count': 0})
        dish.avg_rating = stats['avg_rating']
        dish.review_count = stats['review_count']
        menu_sections[dish.section].append(dish)

    # Define the desired order of sections
    section_order = ['Breakfast', 'Lunch', 'Dinner',
                     'Drinks', 'Daily Specials', 'Other']
    sorted_menu_sections = {key: menu_sections[key]
                            for key in section_order if key in menu_sections}
    return render_template('menu.html', menu_sections=sorted_menu_sections)


@app.route('/add_to_cart/<int:dish_id>', methods=['POST'])
@login_required
def add_to_cart(dish_id):
    try:
        dish = Dish.query.get(dish_id)
        if not dish:
            flash('Dish not found!')
            return redirect(url_for('menu'))
        item = CartItem.query.filter_by(
            user_id=current_user.id, dish_id=dish_id).first()
        if item:
            item.quantity += 1
        else:
            item = CartItem(user_id=current_user.id,
                            dish_id=dish_id, quantity=1)
            db.session.add(item)
        db.session.commit()
        flash('Added to cart!')
        return redirect(url_for('menu'))
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        db.session.rollback()
        flash('Error adding to cart!')
        return redirect(url_for('menu'))


@app.route('/dish/<int:dish_id>', methods=['GET'])
@login_required
def dish_detail(dish_id):
    try:
        dish = Dish.query.get_or_404(dish_id)
        form = ReviewForm()
        reviews = Review.query.filter_by(dish_id=dish_id).order_by(
            Review.created_at.desc()).all()
        # Calculate average rating and review count
        from sqlalchemy import func
        stats = db.session.query(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).filter(Review.dish_id == dish_id, Review.rating.isnot(None)).first()
        dish.avg_rating = stats.avg_rating or 0
        dish.review_count = stats.review_count
        return render_template('dish_detail.html', dish=dish, review_form=form, reviews=reviews)
    except Exception as e:
        print(f"Error in dish_detail: {e}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while loading the dish details.')
        return redirect(url_for('menu'))


@app.route('/dish/<int:dish_id>/review', methods=['POST'])
@login_required
def submit_review(dish_id):
    try:
        dish = Dish.query.get_or_404(dish_id)
        form = ReviewForm()
        reviews = Review.query.filter_by(dish_id=dish_id).order_by(
            Review.created_at.desc()).all()
        if form.validate_on_submit():
            rating = form.rating.data
            review = Review(user_id=current_user.id, dish_id=dish_id,
                            rating=int(rating) if rating else None, review_text=form.review_text.data)
            db.session.add(review)
            db.session.commit()
            flash('Review submitted!')
            return redirect(url_for('dish_detail', dish_id=dish_id))
        else:
            flash('Please select a rating.')
            # Calculate average rating and review count for the template
            valid_ratings = [r.rating for r in reviews if r.rating is not None]
            avg_rating = sum(valid_ratings) / \
                len(valid_ratings) if valid_ratings else 0
            review_count = len(reviews)
            dish.avg_rating = avg_rating
            dish.review_count = review_count
            return render_template('dish_detail.html', dish=dish, review_form=form, reviews=reviews)
    except Exception as e:
        print(f"Error in submit_review: {e}")
        db.session.rollback()
        flash('An error occurred while submitting the review.')
        return redirect(url_for('dish_detail', dish_id=dish_id))


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    items = []
    total = 0
    for item in cart_items:
        dish = Dish.query.get(item.dish_id)
        if dish:
            subtotal = dish.price * item.quantity
            total += subtotal
            items.append({
                'dish': dish,
                'quantity': item.quantity,
                'subtotal': subtotal,
                'cart_item_id': item.id
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
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            flash('Your cart is empty!')
            return redirect(url_for('cart'))
        total = 0
        order = Order(user_id=current_user.id, total=0, status='pending')
        db.session.add(order)
        db.session.flush()  # get order.id
        for item in cart_items:
            dish = Dish.query.get(item.dish_id)
            if dish:
                subtotal = dish.price * item.quantity
                total += subtotal
                order_item = OrderItem(
                    order_id=order.id, dish_id=dish.id, quantity=item.quantity, price=dish.price)
                db.session.add(order_item)
                db.session.delete(item)
        discount = float(request.form.get('discount', 0))
        order.total = total - discount
        points_earned = int(total - discount)  # 1 point per $1 spent
        order.points_earned = points_earned
        current_user.points += points_earned
        if 'redeem_points' in session:
            # Clear redeemed points after checkout
            session.pop('redeem_points')
        db.session.commit()
        return render_template('order_confirmation.html', order=order, discount=discount)
    except Exception as e:
        print(f"Error in checkout: {e}")
        db.session.rollback()
        flash('An error occurred during checkout.')
        return redirect(url_for('cart'))


@app.route('/cart/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    try:
        item = CartItem.query.get_or_404(cart_item_id)
        if item.user_id != current_user.id:
            flash('Unauthorized')
            return redirect(url_for('cart'))
        quantity = int(request.form['quantity'])
        if quantity < 1:
            db.session.delete(item)
        else:
            item.quantity = quantity
        db.session.commit()
        flash('Cart updated!')
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error in update_cart_item: {e}")
        db.session.rollback()
        flash('Error updating cart!')
        return redirect(url_for('cart'))


@app.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_cart_item(cart_item_id):
    try:
        item = CartItem.query.get_or_404(cart_item_id)
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            flash('Item removed from cart!')
        else:
            flash('Unauthorized')
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error in remove_cart_item: {e}")
        db.session.rollback()
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
        if User.query.filter(User.username == username, User.id != current_user.id).first():
            flash('Username already taken')
        elif User.query.filter(User.email == email, User.id != current_user.id).first():
            flash('Email already taken')
        else:
            current_user.username = username
            current_user.email = email
            if password:
                current_user.password = generate_password_hash(password)
            db.session.commit()
            flash('Profile updated!')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user)


@app.route('/claim_admin', methods=['GET', 'POST'])
@login_required
def claim_admin():
    if request.method == 'POST':
        code = request.form.get('admin_code', '')
        if code == app.config.get('ADMIN_CLAIM_CODE'):
            current_user.is_admin = True
            db.session.commit()
            flash('You have been granted admin privileges.')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin code.')
            return redirect(url_for('claim_admin'))
    return render_template('claim_admin.html')

# --- CLI Commands ---


def seed_database():
    if Dish.query.first():
        print('Dishes already exist. Skipping seeding.')
        return
    dishes = [
        # Breakfast
        Dish(section="Breakfast", name="Classic Breakfast", price=9.99, description="Eggs, toast, and more.",
             image_filename=None),
        Dish(section="Breakfast", name="Pancake Stack", price=7.99, description="Fluffy pancakes with syrup.",
             image_filename=None),
        Dish(section="Breakfast", name="Avocado Toast", price=8.50, description="Sourdough with smashed avocado.",
             image_filename=None),
        Dish(section="Breakfast", name="Oatmeal Bowl", price=6.50, description="Healthy oatmeal with fruit.",
             image_filename=None),
        # Lunch
        Dish(section="Lunch", name="Chicken Sandwich", price=12.50, description="Grilled chicken sandwich.",
             image_filename=None),
        Dish(section="Lunch", name="Burger Deluxe", price=14.75, description="Juicy beef burger.",
             image_filename=None),
        Dish(section="Lunch", name="Caesar Salad", price=10.00, description="Classic Caesar salad.",
             image_filename=None),
        Dish(section="Lunch", name="Veggie Wrap", price=11.50, description="Fresh veggie wrap.",
             image_filename=None),
        # Dinner
        Dish(section="Dinner", name="Spaghetti & Meatballs", price=16.99, description="Classic spaghetti with meatballs.",
             image_filename=None),
        Dish(section="Dinner", name="Grilled Salmon", price=18.50, description="Grilled salmon fillet.",
             image_filename=None),
        Dish(section="Dinner", name="Ribeye Steak", price=25.00, description="Juicy ribeye steak.",
             image_filename=None),
        Dish(section="Dinner", name="Chicken Parmesan", price=17.50, description="Breaded chicken with cheese.",
             image_filename=None)
    ]
    db.session.bulk_save_objects(dishes)
    db.session.commit()
    print('Seeded dishes!')


@app.cli.command('seed')
def seed():
    db.create_all()
    seed_database()


# Make the first user an admin (run once)
@app.cli.command('make_admin')
def make_admin():
    with app.app_context():
        user = User.query.first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f'User {user.username} is now an admin.')
        else:
            print('No user found. Please register first.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
