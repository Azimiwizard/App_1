from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, TextAreaField, SelectField, SubmitField, RadioField
from wtforms.validators import DataRequired, NumberRange, ValidationError, InputRequired
from models import Dish


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
        if Dish.query.filter_by(name=field.data).first():
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
