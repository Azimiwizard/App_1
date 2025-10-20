from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, TextAreaField, SelectField, SubmitField, RadioField, PasswordField
from wtforms.validators import DataRequired, NumberRange, ValidationError, InputRequired, Email, Length
from db import get_all_dishes, get_all_users


class DishForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[
                       DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    section = SelectField('Section', choices=[
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Drinks', 'Drinks'),
        ('Daily Specials', 'Daily Specials'),
        ('Other', 'Other')
    ], validators=[DataRequired()])

    def validate_name(self, field):
        dishes = get_all_dishes()
        if any(dish['name'].lower() == field.data.lower() for dish in dishes):
            raise ValidationError('Dish name must be unique.')


class ReviewForm(FlaskForm):
    rating = RadioField('Rating', choices=[
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    ])
    review_text = TextAreaField('Review (optional)')
    submit = SubmitField('Submit Review')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    admin_code = PasswordField('Admin Code (Optional)')

    def validate_username(self, field):
        users = get_all_users()
        if any(user['username'].lower() == field.data.lower() for user in users):
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        users = get_all_users()
        if any(user['email'].lower() == field.data.lower() for user in users):
            raise ValidationError('Email already registered.')
