from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, TextAreaField, FileField, ValidationError
from wtforms.validators import DataRequired, Optional


def decode_bytes(bytes_text):
    encs, res = ["utf-8", "utf-16", "windows-1251", "iso"], ""
    for enc in encs:
        try:
            res = str(bytes_text, enc)
            if "????????" in res or "�" in res:
                res = ""
        except:
            continue
        if res:
            break
    if not res:
        return None
    return res


class Optionals:
    def __init__(self, fields, message="Одно из полей должно быть заполнено."):
        self.fields = fields
        self.message = message

    def __call__(self, form, field):
        fs = [form[i] for i in (self.fields + [field.name])]
        if all(map(lambda a: not a.data, fs)):
            raise ValidationError(self.message)


class IsFileText:
    def __call__(self, form, field):
        if field.data:
            text = decode_bytes(field.data.stream.read())
            field.data.stream.seek(0)
            if not text:
                raise ValidationError("Неизвестная кодировка!")


class AddPageForm(FlaskForm):
    name = StringField('Название главы', validators=[DataRequired()])
    text = TextAreaField('Текст', validators=[Optionals(["file", ])])
    file = FileField("Файл главы(необязательно)", validators=[Optionals(["text", ]), IsFileText()])
    submit = SubmitField('Опубликовать')
