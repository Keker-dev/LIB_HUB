from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, SelectField, ColorField, \
    RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, NumberRange


class SettingsForm(FlaskForm):
    change_name = StringField('Изменить имя пользователя', validators=[Optional()])
    change_pass = PasswordField('Изменить пароль',
                                validators=[Optional(), Length(min=6, message="Пароль должен быть >= 6 символов.")])
    change_about = TextAreaField('Изменить описание', validators=[Optional()])
    font = SelectField("Шрифт", validators=[Optional()],
                       choices=[('Verdana', 'Verdana'), ('Arial', 'Arial'), ('Calibri', 'Calibri')])
    font_color = ColorField("Цвет шрифта", validators=[Optional()])
    font_size = IntegerField('Размер шрифта', validators=[Optional(), NumberRange(min=1, max=100)])
    ignore = SelectField("Какие уведомления игнорировать", validators=[Optional()],
                         choices=[('Все', 'Все'), ('Комментарии к моим работам', 'Комментарии к моим работам'),
                                  ('Никакие', 'Никакие')])
    check_books = IntegerField("Какое кол-во просмотренных работ отслеживать",
                               validators=[Optional(), NumberRange(min=0, max=100)])
    tabs_class = RadioField("", choices=[("1", "Настройки аккаунта"),
                                               ("2", "Настройки оформления"),
                                               ("3", "Токены API"),
                                               ("4", "Дополнительно")], default='1')
    add_token = SubmitField('Добавить токен')
    rem_token = SubmitField('-')
    submit = SubmitField('Подтвердить изменения')
    logout = SubmitField('Выйти из аккаунта')
    del_acc = SubmitField('Удалить аккаунт')
    del_history = SubmitField('Удалить историю просмотров')
