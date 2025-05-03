from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class ProfileForm(FlaskForm):
    submit = SubmitField('Редактировать')
    like = SubmitField('Лайк')
    favorite = SubmitField('В любимое')
