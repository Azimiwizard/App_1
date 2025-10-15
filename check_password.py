import os
from flask import Flask
from werkzeug.security import check_password_hash
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-secure-random-string-that-you-should-replace'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath("instance/stitch_menu.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    user = User.query.first()
    if user:
        print(f'User: {user.username}')
        print(f'Email: {user.email}')
        print(f'Is Admin: {user.is_admin}')
        print(f'Password Hash: {user.password}')

        # Test the password
        test_password = 'admin123'
        if check_password_hash(user.password, test_password):
            print(f'Password "{test_password}" is CORRECT')
        else:
            print(f'Password "{test_password}" is INCORRECT')
    else:
        print('No user found.')
