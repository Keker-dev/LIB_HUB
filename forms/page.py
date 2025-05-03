from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Optional


class PageForm(FlaskForm):
    next = SubmitField('Следующая')
    prev = SubmitField('Назад')
    comm_field = StringField("Написать комментарий", validators=[Optional()])
    comm_sub = SubmitField('Отправить')
    like = StringField('Лайк')
