import os
from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-secure-random-string-that-you-should-replace'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath("instance/stitch_menu.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    user = User.query.first()
    if user:
        new_password = 'admin123'  # You can change this to any password you want
        user.password = generate_password_hash(
            new_password, method='pbkdf2:sha256')
        db.session.commit()
        print(
            f'Password for user {user.username} has been reset to: {new_password}')
    else:
        print('No user found. Please register first.')
