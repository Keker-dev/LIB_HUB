from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class MainPageForm(FlaskForm):
    reg = SubmitField('Зарегистрироваться')
    log = SubmitField('Вход')
    profile = SubmitField(" ")
    settings = SubmitField(" ")
    add_book = SubmitField("Добавить книгу")
    search = StringField("Поиск книг")
    search_submit = SubmitField("")
