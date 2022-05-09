from flask import render_template, redirect, request, url_for, flash, session
from .. import db
from flask_security import login_user, logout_user, login_required, current_user
from . import auth
from app.models import Fan, FanID
from .forms import LoginForm, RegistrationForm, ChangeEmailForm
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint != 'static' \
                and 'buy' in request.endpoint:
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed or ('buy' in request.endpoint):
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ Авторизация """
    form = LoginForm()
    if form.validate_on_submit():
        try:  # проверка типа введёных данных
            login_data = int(form.login.data)
            user = Fan.query.filter((Fan.id == login_data) | (Fan.phone_number == login_data)).first()
        except:
            login_data = form.login.data
            user = Fan.query.filter((Fan.email == login_data) | (Fan.full_name == login_data)).first()
        if (user is not None) and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Неверный логин или пароль')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """ Выход """
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])  # регистрация
def register():
    """ Регистрация """
    form = RegistrationForm()
    if form.validate_on_submit():
        create_fan_id = FanID(full_name=form.full_name.data)  # добавление FanID в БД
        db.session.add(create_fan_id)
        passport = FanID.query.filter_by(number=form.fanID.data).first()
        if passport is not None:
            user = Fan(id=form.fanID.data,
                       full_name=form.full_name.data,
                       phone_number=form.phone.data,
                       email=form.email.data,
                       password_hash=form.password.data
                       )
            user.password(form.password.data)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(user.email, 'Подтверждение электронной почты',
                       'auth/email/confirm', user=user, token=token)
            flash('Вам было отправлено электронное письмо с подтверждением по электронной почте.')
            return redirect(url_for('auth.login'))
        else:
            flash("Такого FanID не существует")
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """ Подтверждение почты """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('Вы подтвердили свою учетную запись. Спасибо!')
    else:
        flash('Ссылка для подтверждения недействительна или срок ее действия истек.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Подтвердите ваш электронный адрес',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('Вам было отправлено электронное письмо с инструкциями '
                  'по подтверждению вашего нового адреса электронной почты.')
            return redirect(url_for('main.index'))
        else:
            flash('Неправильный email или пароль.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Ваш адрес электронной почты был изменён.')
    else:
        flash('Неверный запрос.')
    return redirect(url_for('main.index'))
