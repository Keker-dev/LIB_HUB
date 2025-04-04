from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired, Optional


class PageForm(FlaskForm):
    next = SubmitField('Следующая')
    prev = SubmitField('Назад')
