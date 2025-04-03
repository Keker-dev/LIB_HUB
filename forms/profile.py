from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ProfileForm(FlaskForm):
    submit = SubmitField('Выйти из аккаунта')
