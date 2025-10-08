from functools import wraps
from collections import defaultdict
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')
# Use Heroku's DATABASE_URL if available, otherwise fall back to local SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///stitch_menu.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Models ---


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    section = db.Column(db.String(50), nullable=False, default='Other')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'))
    quantity = db.Column(db.Integer, default=1)


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
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        image_url = request.form['image_url']
        section = request.form['section']
        db.session.add(Dish(name=name, price=price, description=description,
                       image_url=image_url, section=section))
        db.session.commit()
        flash('Dish added!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_add_dish.html')

# Edit dish


@app.route('/admin/dish/edit/<int:dish_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = float(request.form['price'])
        dish.description = request.form['description']
        dish.image_url = request.form['image_url']
        dish.section = request.form['section']
        db.session.commit()
        flash('Dish updated!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_dish.html', dish=dish)

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
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
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
    dishes = Dish.query.all()
    menu_sections = defaultdict(list)
    for dish in dishes:
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
    item = CartItem.query.filter_by(
        user_id=current_user.id, dish_id=dish_id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=current_user.id, dish_id=dish_id, quantity=1)
        db.session.add(item)
    db.session.commit()
    flash('Added to cart!')
    return redirect(url_for('menu'))


@app.route('/dish/<int:dish_id>')
@login_required
def dish_detail(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    return render_template('dish_detail.html', dish=dish)


@app.route('/cart')
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

    return render_template('cart.html', items=items, total=total)


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!')
        return redirect(url_for('cart'))
    total = 0
    order = Order(user_id=current_user.id, total=0)
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
    order.total = total
    db.session.commit()
    return render_template('order_confirmation.html', order=order)


@app.route('/cart/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    item = CartItem.query.get_or_404(cart_item_id)
    if item.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for('cart'))
    try:
        quantity = int(request.form['quantity'])
        if quantity < 1:
            db.session.delete(item)
        else:
            item.quantity = quantity
        db.session.commit()
        flash('Cart updated!')
    except Exception:
        flash('Invalid quantity')
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_cart_item(cart_item_id):
    item = CartItem.query.get_or_404(cart_item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from cart!')
    else:
        flash('Unauthorized')
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


# --- CLI Commands ---
@app.cli.command('seed')
def seed():
    db.create_all()
    if Dish.query.first():
        print('Dishes already exist. Skipping seeding.')
        return
    dishes = [
        # Breakfast
        Dish(section="Breakfast", name="Classic Breakfast", price=9.99, description="Eggs, toast, and more.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuAJh0DPRJwiTIFhPK5fnjUB6w-8C4bztgynoRU20C57Uci8r0D4t0lnIUOz3VeuIsPM90nH9yLw6Y3BewarsxbAKy-zvtrv58kft0RESCu0a_RHCBErw2VSXR48gNE9xp4owZx7fRA1cdX0596gg6bWIiXp1Gc5E40SIOevNTDhzZCvZSdNQ_qMMjlFPy2jeSkAND8Z63oNgtSxCzCJTI8i7t_MRtLeSh4qcUB_YxZ4oe7HGP7TQQmbPiDKhV34dRtzoR9VGnnyFFQ"),
        Dish(section="Breakfast", name="Pancake Stack", price=7.99, description="Fluffy pancakes with syrup.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuDmVMyYU2OgWFMbZRd0t2E8r17ANCeb69w8qQDpkWSvCWa7-F8loC0spRcYGLAwK-w2W4UIXmrrHTKHct0gUS6MpetJo22kx-UPzNfdyWE_Q9JNnVG6d3RkmDFevE0k5jJVkocgBOHDpNpSxxJHAQwU3Fay1Mt2mqIIq1sZgbTG6FlC4S0YKzKARJUOH8ve4lko5TiK2cLa8KF-US6wcdh5HGW4uivOteX44TzzKE19x3s0W429ssdKNu1WWATfOoADynIOuchl3pQ"),
        Dish(section="Breakfast", name="Avocado Toast", price=8.50, description="Sourdough with smashed avocado.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuAFY5KTEJ7DutOOVYusMnP8LscjlKBf5YPiUitX5Kv-BCb2EWePUPudkfR4pKMJ_f94SiEBNQPH70FpqVFSW5HFTxlMmjgiWaZL5p8ot7c6Any9erxYm0dTCl-au8DEAuz_IkLdg3TdyhNZaCRaHaMEgRnS7tes5695jeRLNEYahJoRSs1jH3EYwMLIv7DdaM-zuzmEqjoLKw_L32H0iJqPHsk5t_Tm__Oi8tmGOsdNn1nOctw4TkxI3WPCVU9vNiRV0XWLL2z8vD0"),
        Dish(section="Breakfast", name="Oatmeal Bowl", price=6.50, description="Healthy oatmeal with fruit.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuD89grVa6a6LRLaCfOmZ1eU-TVfHvz7Z12fHkRfHVEE8pydj5NId8IuJXmgyeAdu4DRXeB67NHEFOfhTgQjKonwT6Y6BW-7ZB8WhAN8lgf9HslkpBxBq2SGubTnr1QIkxrrzLLU8dsmmSKrW8gdP8qVzGl9nKOZmQ98IAO7efTJImsIAQqAHcsZLqukeoQOsDhCMy05JWJ4mrJEB_1Jw3GMpnC4b46096UqahzcfUaeZndROeJATEWmjkxBqFO3W66DDVhRXJ9_YMs"),
        # Lunch
        Dish(section="Lunch", name="Chicken Sandwich", price=12.50, description="Grilled chicken sandwich.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuA6SPn3c9jwo37E8XnFbDdfBemrnT162S6x6JwEFZBJXoNKLDXA-16blw3vFUSdqsTi5JTYBvFZQ7aK7UgQ913lkE1nIqLaRYEplev_z_AKaHuIzPKRZBAqBzez9ejbJJdbJpJD9fytQd1YOU1Wd2QB07aQsL7Ssl1UjyJG_saq2V6YrCmEOJdyGj7muiupF90x9u0pclksrsp39D2ekorxpFr5aryTlzCorBDYqkiMP9rmdyzUQIRh1vnIivwIz6CbqhTCq5mh1CA"),
        Dish(section="Lunch", name="Burger Deluxe", price=14.75, description="Juicy beef burger.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuAnm1viCEuwGWCRwRUn-njhoILHC4NTVwb12MeCPJR77bO5l9p7kBeCPrgWa0ooE2H8IUHzIpqxKzBisgSQoKE6Djh71nBV_74lUtsNLxoeJNplscfpJgXpMXzgWXqc2oQdI21LWq7TNO1ICYQ5jaV3PFYz3dM3KAupplbbUgyiyjG44epHMFR-3u7LCWjmpCImeYNzs5v49RgkPAabO9SIOGXZ1ljAcSnBAN6cEpRLL5p9hdiRYMzdisfPLaVoOJmNrUZWAQMUjps"),
        Dish(section="Lunch", name="Caesar Salad", price=10.00, description="Classic Caesar salad.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuCsVW-fvmvEf3CVC8u3mgMRBj8pQRfMyiHH-7eyBVdqN-xwuH83hR-5v1OSJmGO4WzQYr56lHiDew5djsu7gOIjOmZd1kX765aEfrFQZhi6Bjoo0MzUUBMl5PQ_1RpSNVDDuVFB13aMFhcr52Npz1RVkZHNcX_1Ky72LmcQlCGlScf09Fv_OYNd7aNE5f1g9a13RseJBV2v-GqVR87IKfUdMWV8MD-m8W_rEJg4jSYfcVi2K_HpVDk06I0w3ztO3RaNLqBmElGa9L4"),
        Dish(section="Lunch", name="Veggie Wrap", price=11.50, description="Fresh veggie wrap.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuANnMQXTQmXdzKhu4NGBm-uRDGFo3c6W9VCSQ2riv0vvgjcNrE0CrH_qG0MSiFOw0iHdRm6pjkR4peLWIcvZuJtbD3lmrnbcvYfv1p6keM9ruR5x_yJJczjQhYoi-cyeVqziUu63FBNEadtuyhAu9XA3KYOIXxOK6UXf4et6dONzXZpwNIN7yhio3lH-NRc0aDKEPnk57Mh9Mh6k_EiWTaQO2TfrAo8BTfyD_sYZgKBKnbJAYpiaDBqggjp7RjX59Xn8YnZh9y21ok"),
        # Dinner
        Dish(section="Dinner", name="Spaghetti & Meatballs", price=16.99, description="Classic spaghetti with meatballs.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuAF-Vu9hmDT5IwjoF4OeVw1x01X91EJsQeenM98KLaB4BM7UxR7HqZeO0sLRXrkXzrcurV-ZHVcH05asOGFgGnV9VvIR_TxkgSuq1YoHPFm_fcnvX7DW8eos-Yd0TEIs6cQywpWw-2Jb9esgDX6SLJDPuXmbd2jbcLMlbi3yrdT3Ke4LgmUnt3zZ6fr3y6MENG_QwF1glSgOGm6GbDFMsOTQ05FWJZLIVPoxvVjVM1AbC6C0xNzLqdgqNYl5w0pMh2J0N01t8l3P74"),
        Dish(section="Dinner", name="Grilled Salmon", price=18.50, description="Grilled salmon fillet.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuBG41f0rfJLO_eD__LFGCJoIbmo2imGJQVRCVv3SlPN-d_27AE0UmIok7myoVq5201LHPJtz1hEb3EoeVRztn1x3fa30irrT2zaX9GYcnHhf3F-Qq97T45OqIwdO5cP-wfup6CVQL3XqkCm1LpI9hf9GFBlBePHXrc1qwMiF4GZZCN3qiVvayGBj3qEDd40YGQyduHIa74KNgexHaiOsVP9jTIJ49KbmR71gBmgkKRajUGWIjU5cb1k6P2oUpkJVtI9p6pprqI9gfQ"),
        Dish(section="Dinner", name="Ribeye Steak", price=25.00, description="Juicy ribeye steak.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuCPSJpmjlLSTRPx6kGAnc21csfda0P8h3lVViCw49kIJLKIICbDDl8djOgsR-O3jOLTXbTMCi-e2LjaQaZqSPTGCH-L6740aO3vCe-mHfhArHvrWKaBOzKBSZNoIFB74Dh96ZHkeSiiWfO4vgTFbZ3GepYM2I2_LjhCdqFYDkx1rPZN7OAnDP9r3mt-7FqPphv9qOz9y-ZJbBmfPC5CdOg3ohYHzxP2uW00sj2tmMV7szJtVt7Qx9sNUFABh2KX3_gRRRlRK4F4ucY"),
        Dish(section="Dinner", name="Chicken Parmesan", price=17.50, description="Breaded chicken with cheese.",
             image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuD8HzoAlTwS2y9F2UwlCc7rDv8E4dzrBQmgpsusR_GOZdcdSodgSajyjU0u6TldoblpaFyJ_FRSn4sIDQWoKnVzsOo3XBYVAAQ5TKDvnTw5cH1tI-x-6JGyTei4g7VsJRb7WhzlsDshO-JECl23cYf2lA3268i_gn0VJocLjl4ddu1xoynNKaS5FtqJLzernKWiFyy7dbrBW6tuz8iqutzBwZlOU2Z4U5zsPWSIVhabz9x8FQz4D2VefNJXRN0g6FIpn_o8JTgKvJo")
    ]
    db.session.bulk_save_objects(dishes)
    db.session.commit()
    print('Seeded dishes!')


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
    app.run(debug=True)

# Ensure database tables are created on app startup in production
with app.app_context():
    db.create_all()
