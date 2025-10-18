import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

load_dotenv()

supabase_url = os.environ.get('SUPABASE_URL')
supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_service_role_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_anon_key:
    raise ValueError("Supabase credentials not found in environment variables")

supabase: Client = create_client(supabase_url, supabase_anon_key)
supabase_admin: Client = create_client(
    supabase_url, supabase_service_role_key) if supabase_service_role_key else None

# Table names
TABLE_USERS = 'users'
TABLE_DISHES = 'dish'
TABLE_ORDERS = 'order'
TABLE_ORDER_ITEMS = 'order_item'
TABLE_CART_ITEMS = 'cart_item'
TABLE_REVIEWS = 'review'

# User operations


def get_user_by_auth_id(auth_user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by Supabase Auth user ID"""
    try:
        response = supabase.table(TABLE_USERS).select(
            '*').eq('auth_user_id', auth_user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user by auth ID: {e}")
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        response = supabase.table(TABLE_USERS).select(
            '*').eq('email', email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        response = supabase.table(TABLE_USERS).select(
            '*').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None


def create_user(auth_user_id: str, username: str, email: str, is_admin: bool = False) -> Optional[Dict[str, Any]]:
    """Create a new user"""
    try:
        user_data = {
            'id': str(uuid.uuid4()),
            'auth_user_id': auth_user_id,
            'username': username,
            'email': email,
            'is_admin': is_admin,
            'points': 0
        }
        response = supabase.table(TABLE_USERS).insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def update_user(user_id: str, updates: Dict[str, Any]) -> bool:
    """Update user data"""
    try:
        response = supabase.table(TABLE_USERS).update(
            updates).eq('id', user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating user: {e}")
        return False


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users"""
    try:
        response = supabase.table(TABLE_USERS).select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []

# Dish operations


def get_all_dishes() -> List[Dict[str, Any]]:
    """Get all dishes"""
    try:
        client = supabase_admin if supabase_admin else supabase
        response = client.table(TABLE_DISHES).select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error getting all dishes: {e}")
        return []


def get_dish_by_id(dish_id: str) -> Optional[Dict[str, Any]]:
    """Get dish by ID"""
    try:
        client = supabase_admin if supabase_admin else supabase
        response = client.table(TABLE_DISHES).select(
            '*').eq('id', dish_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting dish by ID: {e}")
        return None


def create_dish(name: str, price: float, description: str = None, image_filename: str = None, section: str = None) -> Optional[Dict[str, Any]]:
    """Create a new dish"""
    try:
        dish_data = {
            'id': str(uuid.uuid4()),
            'name': name,
            'price': price,
            'description': description,
            'image_filename': image_filename,
            'section': section
        }
        # Use admin client if available for bypassing RLS
        client = supabase_admin if supabase_admin else supabase
        response = client.table(TABLE_DISHES).insert(dish_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating dish: {e}")
        return None


def update_dish(dish_id: str, updates: Dict[str, Any]) -> bool:
    """Update dish data"""
    try:
        client = supabase_admin if supabase_admin else supabase
        response = client.table(TABLE_DISHES).update(
            updates).eq('id', dish_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating dish: {e}")
        return False


def delete_dish(dish_id: str) -> bool:
    """Delete a dish"""
    try:
        client = supabase_admin if supabase_admin else supabase
        # Delete related records first to avoid foreign key constraints
        client.table(TABLE_ORDER_ITEMS).delete().eq(
            'dish_id', dish_id).execute()
        client.table(TABLE_CART_ITEMS).delete().eq(
            'dish_id', dish_id).execute()
        client.table(TABLE_REVIEWS).delete().eq('dish_id', dish_id).execute()
        # Now delete the dish
        response = client.table(TABLE_DISHES).delete().eq(
            'id', dish_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error deleting dish: {e}")
        return False

# Cart operations


def get_cart_items(user_id: str) -> List[Dict[str, Any]]:
    """Get cart items for a user"""
    try:
        response = supabase.table(TABLE_CART_ITEMS).select(
            '*, dish(*)').eq('user_id', user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting cart items: {e}")
        return []


def add_to_cart(user_id: str, dish_id: str, quantity: int = 1) -> Optional[Dict[str, Any]]:
    """Add item to cart or update quantity if exists"""
    try:
        # Check if item already exists
        existing = supabase.table(TABLE_CART_ITEMS).select(
            '*').eq('user_id', user_id).eq('dish_id', dish_id).execute()

        if existing.data:
            # Update quantity
            new_quantity = existing.data[0]['quantity'] + quantity
            response = supabase.table(TABLE_CART_ITEMS).update(
                {'quantity': new_quantity}).eq('id', existing.data[0]['id']).execute()
            return response.data[0] if response.data else None
        else:
            # Create new cart item
            cart_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'dish_id': dish_id,
                'quantity': quantity
            }
            response = supabase.table(
                TABLE_CART_ITEMS).insert(cart_data).execute()
            return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return None


def update_cart_item(cart_item_id: str, quantity: int) -> bool:
    """Update cart item quantity"""
    try:
        if quantity <= 0:
            response = supabase.table(TABLE_CART_ITEMS).delete().eq(
                'id', cart_item_id).execute()
        else:
            response = supabase.table(TABLE_CART_ITEMS).update(
                {'quantity': quantity}).eq('id', cart_item_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating cart item: {e}")
        return False


def remove_cart_item(cart_item_id: str) -> bool:
    """Remove item from cart"""
    try:
        response = supabase.table(TABLE_CART_ITEMS).delete().eq(
            'id', cart_item_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error removing cart item: {e}")
        return False


def clear_cart(user_id: str) -> bool:
    """Clear all cart items for a user"""
    try:
        response = supabase.table(TABLE_CART_ITEMS).delete().eq(
            'user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error clearing cart: {e}")
        return False

# Order operations


def create_order(user_id: str, total: float, phone_number: str = None) -> Optional[Dict[str, Any]]:
    """Create a new order"""
    try:
        order_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'phone_number': phone_number,
            'total': total,
            'status': 'pending',
            'points_earned': int(total)  # 1 point per dollar
        }
        response = supabase.table(TABLE_ORDERS).insert(order_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating order: {e}")
        return None


def get_orders_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Get orders for a user"""
    try:
        response = supabase.table(TABLE_ORDERS).select(
            '*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting orders by user: {e}")
        return []


def get_all_orders() -> List[Dict[str, Any]]:
    """Get all orders (admin)"""
    try:
        response = supabase.table(TABLE_ORDERS).select(
            '*').order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting all orders: {e}")
        return []


def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
    """Get order by ID"""
    try:
        response = supabase.table(TABLE_ORDERS).select(
            '*').eq('id', order_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting order by ID: {e}")
        return None


def update_order_status(order_id: str, status: str) -> bool:
    """Update order status"""
    try:
        response = supabase.table(TABLE_ORDERS).update(
            {'status': status}).eq('id', order_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating order status: {e}")
        return False


def create_order_item(order_id: str, dish_id: str, quantity: int, price: float) -> Optional[Dict[str, Any]]:
    """Create an order item"""
    try:
        item_data = {
            'id': str(uuid.uuid4()),
            'order_id': order_id,
            'dish_id': dish_id,
            'quantity': quantity,
            'price': price
        }
        response = supabase.table(
            TABLE_ORDER_ITEMS).insert(item_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating order item: {e}")
        return None


def get_order_items(order_id: str) -> List[Dict[str, Any]]:
    """Get order items for an order"""
    try:
        response = supabase.table(TABLE_ORDER_ITEMS).select(
            '*, dish(*)').eq('order_id', order_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting order items: {e}")
        return []

# Review operations


def get_reviews_by_dish(dish_id: str) -> List[Dict[str, Any]]:
    """Get reviews for a dish"""
    try:
        response = supabase.table(TABLE_REVIEWS).select(
            '*, users(*)').eq('dish_id', dish_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting reviews by dish: {e}")
        return []


def create_review(user_id: str, dish_id: str, rating: int, review_text: str = None) -> Optional[Dict[str, Any]]:
    """Create a new review"""
    try:
        review_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'dish_id': dish_id,
            'rating': rating,
            'review_text': review_text
        }
        response = supabase.table(TABLE_REVIEWS).insert(review_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating review: {e}")
        return None


def get_review_stats() -> Dict[str, Dict[str, Any]]:
    """Get review statistics for all dishes"""
    try:
        # This would need to be implemented with Supabase's RPC or multiple queries
        # For now, return empty dict - we'll calculate this in the application layer
        return {}
    except Exception as e:
        print(f"Error getting review stats: {e}")
        return {}

# Utility functions


def calculate_review_stats(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate average rating and review count from reviews"""
    if not reviews:
        return {'avg_rating': 0, 'review_count': 0}

    valid_ratings = [r['rating']
                     for r in reviews if r.get('rating') is not None]
    if not valid_ratings:
        return {'avg_rating': 0, 'review_count': len(reviews)}

    avg_rating = sum(valid_ratings) / len(valid_ratings)
    return {'avg_rating': avg_rating, 'review_count': len(reviews)}
