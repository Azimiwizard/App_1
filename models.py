from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import url_for

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    reviews = db.relationship('Review', backref='author', lazy=True)

    @property
    def is_active(self):
        return True


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(300))
    section = db.Column(db.String(50), nullable=False, default='Other')

    @property
    def image_url(self):
        if self.image_filename and self.image_filename.startswith('http'):
            return self.image_filename
        elif self.image_filename:
            return '/static/uploads/' + self.image_filename
        return '/static/logo.png'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    points_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'))
    quantity = db.Column(db.Integer, default=1)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', lazy=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 or None
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
