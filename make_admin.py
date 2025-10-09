from main import app, db
from models import User

with app.app_context():
    user = User.query.first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f'User {user.username} is now admin.')
    else:
        print('No user found. Please register first.')
