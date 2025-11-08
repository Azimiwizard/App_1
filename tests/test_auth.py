"""
Test authentication functionality.
"""
import pytest
from flask import session
from models import User


def test_register(client):
    """Test user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Successfully registered' in response.data


def test_login_logout(client):
    """Test login and logout functionality"""
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Logged in successfully' in response.data

    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out successfully' in response.data


def test_invalid_login(client):
    """Test login with invalid credentials"""
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
