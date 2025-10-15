from main import app, db
from models import User
import argparse
import sys


def find_user(username: str = None, email: str = None):
    if email:
        return User.query.filter(db.func.lower(User.email) == email.lower()).first()
    if username:
        return User.query.filter(db.func.lower(User.username) == username.lower()).first()
    return None


def promote_to_admin(user: User):
    if user.is_admin:
        print(f'User {user.username} is already an admin.')
        return 0
    user.is_admin = True
    db.session.commit()
    print(f'User {user.username} is now an admin.')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Promote a user to admin by username or email.')
    parser.add_argument('--username', help='Username of the user to promote')
    parser.add_argument('--email', help='Email of the user to promote')
    args = parser.parse_args()

    if not args.username and not args.email:
        print('Error: Provide --username or --email to identify the user to promote.')
        sys.exit(2)

    with app.app_context():
        user = find_user(username=args.username, email=args.email)
        if not user:
            ident = args.email or args.username
            print(f'Error: User with identifier "{ident}" not found.')
            sys.exit(1)
        sys.exit(promote_to_admin(user))
