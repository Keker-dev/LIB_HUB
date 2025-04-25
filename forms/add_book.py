from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, FileField
from wtforms.validators import DataRequired, Optional, NumberRange, InputRequired


class AddBookForm(FlaskForm):
    name = StringField('Название книги', validators=[DataRequired()])
    about = StringField("Описание", validators=[Optional()])
    price = IntegerField("Цена", validators=[InputRequired(),
                                             NumberRange(min=0, message="Цена не может быть ниже 0!")], default=0)
    is_private = BooleanField("Только для подписчиков", validators=[Optional()])
    file = FileField("Файл книги (необязательно)", validators=[Optional()])
    submit = SubmitField('Опубликовать')
