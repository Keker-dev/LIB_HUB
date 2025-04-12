from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class SettingsForm(FlaskForm):
    change_name = StringField('Изменить имя пользователя', validators=[Optional()])
    font_size = IntegerField('Размер шрифта', validators=[Optional()])
    del_history = SubmitField('Удалить историю просмотров')
