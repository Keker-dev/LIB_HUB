from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired, Optional


class BookForm(FlaskForm):
    add_page = SubmitField('Добавить главу')
    author = SubmitField(' ')
    read = SubmitField('Читать')
