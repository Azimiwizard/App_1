"""
Input validation utilities for the application.
"""
from wtforms.validators import ValidationError
import re


def validate_password_strength(form, field):
    """
    Validate password strength:
    - At least 8 characters
    - Contains at least one digit
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one special character
    """
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')

    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit')

    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            'Password must contain at least one uppercase letter')

    if not re.search(r'[a-z]', password):
        raise ValidationError(
            'Password must contain at least one lowercase letter')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(
            'Password must contain at least one special character')


def validate_username(form, field):
    """
    Validate username:
    - 3-20 characters long
    - Only letters, numbers, and underscores
    - Must start with a letter
    """
    username = field.data
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$', username):
        raise ValidationError(
            'Username must be 3-20 characters long, start with a letter, and contain only letters, numbers, and underscores')


def validate_price(form, field):
    """
    Validate price:
    - Must be a positive number
    - Maximum two decimal places
    """
    try:
        price = float(field.data)
        if price <= 0:
            raise ValidationError('Price must be greater than 0')
        if len(str(price).split('.')[-1]) > 2:
            raise ValidationError(
                'Price cannot have more than 2 decimal places')
    except ValueError:
        raise ValidationError('Invalid price format')


def sanitize_html(text):
    """Remove HTML tags from input"""
    return re.sub(r'<[^>]*?>', '', text)


def validate_image(form, field):
    """
    Validate image upload:
    - File must be present
    - Must be an allowed extension
    - Must not exceed size limit
    """
    if not field.data:
        raise ValidationError('No file uploaded')

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    filename = field.data.filename.lower()

    if not ('.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions):
        raise ValidationError(
            'Invalid file type. Allowed types: png, jpg, jpeg, gif')

    # Max file size check (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    if field.data.content_length > MAX_FILE_SIZE:
        raise ValidationError('File size exceeds maximum limit (5MB)')
