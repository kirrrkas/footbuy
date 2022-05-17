from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from app.models import Fan


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    fanID = IntegerField('FanID', validators=[DataRequired()])
    full_name = StringField('ФИО', validators=[DataRequired()])
    phone = StringField('Номер телефона')
    email = StringField('Эл. почта', validators=[DataRequired(), Length(1, 64),
                                                 Email(message='Неверно введена эл.почта.')])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   EqualTo('password2', message='Пароль должен совпадать.')])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_fanID(self, field):
        if Fan.query.filter_by(id=field.data).first():
            raise ValidationError('Такой FanID уже зарегистрирован.')

    def validate_email(self, field):
        if Fan.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Такая электронная почта уже зарегистрирована.')

    def validate_phone(self, field):
        if Fan.query.filter_by(phone_number=field.data.lower()).first():
            raise ValidationError('Такой номер телефона уже зарегистрирован.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()],
                                 render_kw={"placeholder": "Старый пароль"})
    password = PasswordField('Новый пароль', validators=[
        DataRequired(), EqualTo('password2', message='Пароль должен совпадать.')],
                             render_kw={"placeholder": "Новый пароль"})
    password2 = PasswordField('Повторите новый пароль',
                              validators=[DataRequired()],
                              render_kw={"placeholder": "Повторите новый пароль"})
    submit = SubmitField('Изменить пароль')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Эл. почта',
                        validators=[DataRequired(), Length(1, 64), Email(message='Неверно введена эл.почта.')],
                        render_kw={"placeholder": "Электронная почта"})
    submit = SubmitField('Сбросить пароль')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[
        DataRequired(), EqualTo('password2', message='Пароль должен совпадать.')],
                             render_kw={"placeholder": "Новый пароль"})
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()],
                              render_kw={"placeholder": "Повторите пароль"})
    submit = SubmitField('Изменить пароль')


class ChangeEmailForm(FlaskForm):
    email = StringField('Новый адрес эл.почты', validators=[DataRequired(), Length(1, 64),
                                                            Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить адрес эл.почты')

    def validate_email(self, field):
        if Fan.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Эта электронная почта уже зарегистрирована.')
