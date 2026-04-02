from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class CompositionForm(FlaskForm):
    composition = TextAreaField(validators=[DataRequired()])

class SearchForm(FlaskForm):
    product_name = StringField(validators=[DataRequired()])

class ScanForm(FlaskForm):
    barcode_image = FileField(validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Регистрация')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')