from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange, ValidationError
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
