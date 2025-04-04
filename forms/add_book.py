from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, FileField
from wtforms.validators import DataRequired, Optional


class AddBookForm(FlaskForm):
    name = StringField('Название книги', validators=[DataRequired()])
    price = IntegerField("Цена", validators=[DataRequired()])
    is_private = BooleanField("Только для подписчиков", validators=[Optional()])
    file = FileField("Файл книги (необязательно)", validators=[Optional()])
    submit = SubmitField('Опубликовать')
