from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Optional


class AddPageForm(FlaskForm):
    name = StringField('Название главы', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()])
    date_push = DateTimeField("Дата выхода в доступ(необязательно)", validators=[Optional()])
    submit = SubmitField('Опубликовать')