"""
Test configuration and fixtures for the application.
"""
import os
import pytest
from main import app as flask_app
from db import db, init_db
from models import User


@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key'
    })

    # Initialize database
    with flask_app.app_context():
        db.create_all()

    yield flask_app

    # Cleanup
    with flask_app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client):
    """Client with authenticated user"""
    with flask_app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='testpass',
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()

        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        return client


@pytest.fixture
def admin_client(client):
    """Client with authenticated admin user"""
    with flask_app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash='adminpass',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass'
        })
        return client
