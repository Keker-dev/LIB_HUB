from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, NumberRange


class AuthorForm(FlaskForm):
    tabs_class = RadioField("", choices=[("1", "Уведомления"), ("2", "Мои работы")], default='1')
    add_book = SubmitField("Добавить книгу")