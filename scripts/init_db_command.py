from models import db  # Import db from models, but initialize it
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create app instance for this script
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')
database_url = os.environ.get('DATABASE_URL')
if database_url is None:
    if os.environ.get('PORT'):  # Production environment
        raise RuntimeError(
            "DATABASE_URL environment variable is required for production deployment. Add a PostgreSQL database service in your Railway dashboard.")
    database_url = 'sqlite:///stitch_menu.db'
else:
    database_url = database_url.replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with this app
db.init_app(app)


def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()
