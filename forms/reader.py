from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, NumberRange


class ReaderForm(FlaskForm):
    tabs_class = RadioField("", choices=[("1", "Уведомления"),
                                               ("2", "Просмотренные работы"),
                                               ("3", "Понравившиеся авторы"),
                                               ("4", "Понравившиеся книги")], default='1')