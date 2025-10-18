from main import app
from db import get_user_by_email, update_user
import argparse
import sys


def find_user(username: str = None, email: str = None):
    if email:
        return get_user_by_email(email)
    # For username, we'd need to add a function to get by username
    # For now, just support email
    return None


def promote_to_admin(user):
    if user['is_admin']:
        print(f'User {user["username"]} is already an admin.')
        return 0
    update_user(user['id'], {'is_admin': True})
    print(f'User {user["username"]} is now an admin.')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Promote a user to admin by email.')
    parser.add_argument(
        '--email', help='Email of the user to promote', required=True)
    args = parser.parse_args()

    with app.app_context():
        user = find_user(email=args.email)
        if not user:
            print(f'Error: User with email "{args.email}" not found.')
            sys.exit(1)
        sys.exit(promote_to_admin(user))
