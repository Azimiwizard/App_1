import os
from dotenv import load_dotenv
from supabase import create_client, Client
from models import db, Users, Dish, Order, OrderItem, CartItem, Review
from main import app

load_dotenv()

supabase_url = os.environ.get('SUPABASE_URL')
supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_service_role_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if supabase_url and supabase_anon_key:
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    supabase_admin: Client = create_client(
        supabase_url, supabase_service_role_key)
else:
    raise ValueError("Supabase credentials not found in environment variables")


def init_supabase_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Supabase database tables created successfully.")

        # Seed initial data if needed
        if not Dish.query.first():
            # Add some sample dishes
            dishes = [
                Dish(name="Classic Breakfast", price=9.99,
                     description="Eggs, toast, and more.", section="Breakfast"),
                Dish(name="Pancake Stack", price=7.99,
                     description="Fluffy pancakes with syrup.", section="Breakfast"),
                Dish(name="Chicken Sandwich", price=12.50,
                     description="Grilled chicken sandwich.", section="Lunch"),
                Dish(name="Burger Deluxe", price=14.75,
                     description="Juicy beef burger.", section="Lunch"),
                Dish(name="Spaghetti & Meatballs", price=16.99,
                     description="Classic spaghetti with meatballs.", section="Dinner"),
                Dish(name="Grilled Salmon", price=18.50,
                     description="Grilled salmon fillet.", section="Dinner"),
            ]
            db.session.bulk_save_objects(dishes)
            db.session.commit()
            print("Sample dishes seeded.")


if __name__ == "__main__":
    init_supabase_db()
