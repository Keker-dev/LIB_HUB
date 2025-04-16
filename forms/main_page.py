from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SearchField
from wtforms.validators import DataRequired, Optional


class MainPageForm(FlaskForm):
    reg = SubmitField('Зарегистрироваться')
    log = SubmitField('Вход')
    profile = SubmitField(" ")
    settings = SubmitField(" ")
    add_book = SubmitField("Добавить книгу")
    search = SearchField("Поиск книг", validators=[Optional()])
    search_submit = SubmitField("")
