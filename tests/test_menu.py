"""
Test menu and dish functionality.
"""
import pytest
from models import Dish
from db import db


def test_view_menu(client):
    """Test viewing the menu page"""
    response = client.get('/menu')
    assert response.status_code == 200
    assert b'Menu' in response.data


def test_add_dish(admin_client):
    """Test adding a new dish (admin only)"""
    response = admin_client.post('/admin/add_dish', data={
        'name': 'Test Dish',
        'description': 'A test dish',
        'price': '9.99',
        'section': 'Lunch'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Dish added successfully' in response.data


def test_edit_dish(admin_client, app):
    """Test editing an existing dish"""
    # Create a test dish
    with app.app_context():
        dish = Dish(
            name='Original Dish',
            description='Original description',
            price=10.99,
            section='Dinner'
        )
        db.session.add(dish)
        db.session.commit()
        dish_id = dish.id

    # Edit the dish
    response = admin_client.post(f'/admin/edit_dish/{dish_id}', data={
        'name': 'Updated Dish',
        'description': 'Updated description',
        'price': '12.99',
        'section': 'Dinner'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Dish updated successfully' in response.data

    # Verify the changes
    with app.app_context():
        updated_dish = Dish.query.get(dish_id)
        assert updated_dish.name == 'Updated Dish'
        assert updated_dish.price == 12.99
