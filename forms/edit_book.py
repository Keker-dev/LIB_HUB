from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, FileField
from wtforms.validators import DataRequired, Optional, NumberRange, InputRequired


class EditBookForm(FlaskForm):
    name = StringField('Изменить название книги', validators=[Optional()])
    about = StringField("Описание", validators=[Optional()])
    price = IntegerField("Цена", validators=[Optional(),
                                             NumberRange(min=0, message="Цена не может быть ниже 0!")], default=0)
    photo = FileField("Обложка книги формата 2:3", validators=[Optional()])
    submit = SubmitField('Подтвердить')
