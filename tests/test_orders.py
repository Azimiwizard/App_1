"""
Test order functionality.
"""
import pytest
from models import Order, OrderItem, Dish
from db import db


def test_add_to_cart(auth_client, app):
    """Test adding items to cart"""
    # Create a test dish
    with app.app_context():
        dish = Dish(
            name='Test Dish',
            description='Test description',
            price=9.99,
            section='Lunch'
        )
        db.session.add(dish)
        db.session.commit()
        dish_id = dish.id

    # Add dish to cart
    response = auth_client.post('/add_to_cart', json={
        'dish_id': dish_id,
        'quantity': 2
    })

    assert response.status_code == 200
    assert 'success' in response.get_json()


def test_place_order(auth_client, app):
    """Test placing an order"""
    # Create a test dish and add to cart first
    with app.app_context():
        dish = Dish(
            name='Order Dish',
            description='Order description',
            price=15.99,
            section='Dinner'
        )
        db.session.add(dish)
        db.session.commit()
        dish_id = dish.id

    # Add to cart
    auth_client.post('/add_to_cart', json={
        'dish_id': dish_id,
        'quantity': 1
    })

    # Place order
    response = auth_client.post('/place_order', follow_redirects=True)
    assert response.status_code == 200
    assert b'Order placed successfully' in response.data


def test_view_orders(admin_client):
    """Test viewing orders (admin only)"""
    response = admin_client.get('/admin/orders')
    assert response.status_code == 200
    assert b'Orders' in response.data
