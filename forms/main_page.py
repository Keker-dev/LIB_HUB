from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired


class MainPageForm(FlaskForm):
    reg = SubmitField('Зарегистрироваться')
    log = SubmitField('Вход')
    profile = SubmitField('Профиль')
