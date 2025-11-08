import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    Numeric,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db


class Users(db.Model):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Maps to Supabase Auth user's UUID
    auth_user_id = Column(String(36), unique=True,
                          index=True, nullable=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    # Do NOT store plaintext passwords when using Supabase Auth.
    # Keep a password field only if you manage auth yourself (not recommended).
    password = Column(Text, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)
    # relationships (optional convenience)
    orders = relationship("Order", back_populates="user",
                          cascade="all, delete-orphan")
    cart_items = relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user",
                           cascade="all, delete-orphan")
    # RBAC relation (many-to-many)
    roles = relationship('Role', secondary='user_roles', backref='users')

    def __repr__(self):
        return f"<Users id={self.id} username={self.username} email={self.email}>"


class Dish(db.Model):
    __tablename__ = "dish"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    image_filename = Column(String(255))
    section = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)
    # relationships
    order_items = relationship(
        "OrderItem", back_populates="dish", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="dish",
                           cascade="all, delete-orphan")


class Order(db.Model):
    __tablename__ = "order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(50))
    total = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(50), nullable=False, default="pending")
    points_earned = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)
    user = relationship("Users", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey(
        "order.id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(UUID(as_uuid=True), ForeignKey(
        "dish.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)
    order = relationship("Order", back_populates="order_items")
    dish = relationship("Dish", back_populates="order_items")


class CartItem(db.Model):
    __tablename__ = "cart_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(UUID(as_uuid=True), ForeignKey(
        "dish.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)
    user = relationship("Users", back_populates="cart_items")
    dish = relationship("Dish")


class Review(db.Model):
    __tablename__ = "review"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(UUID(as_uuid=True), ForeignKey(
        "dish.id", ondelete="CASCADE"), nullable=False)
    # validate 1-5 at application layer or use CheckConstraint
    rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)
    user = relationship("Users", back_populates="reviews")
    dish = relationship("Dish", back_populates="reviews")


# RBAC models: roles, permissions, and association tables
role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey(
        'roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', UUID(as_uuid=True), db.ForeignKey(
        'permissions.id', ondelete='CASCADE'), primary_key=True),
)

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey(
        'users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey(
        'roles.id', ondelete='CASCADE'), primary_key=True),
)


class Role(db.Model):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)

    permissions = relationship(
        'Permission', secondary=role_permissions, back_populates='roles')

    def __repr__(self):
        return f"<Role name={self.name}>"


class Permission(db.Model):
    __tablename__ = 'permissions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(150), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)

    roles = relationship('Role', secondary=role_permissions,
                         back_populates='permissions')

    def __repr__(self):
        return f"<Permission code={self.code}>"


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    before_json = Column(Text)
    after_json = Column(Text)
    ip = Column(String(100))
    user_agent = Column(String(500))
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), nullable=False)

    actor = relationship('Users')

    def __repr__(self):
        return f"<AuditLog id={self.id} action={self.action} entity={self.entity}>"
