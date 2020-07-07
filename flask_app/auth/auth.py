import datetime as dt
import os
from base64 import b64encode
from functools import wraps
from typing import Optional

import pytz
from firestore_ci import FirestoreDocument
from flask import flash, redirect, url_for, render_template, request, current_app, Response, make_response
from flask_login import UserMixin, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from wtforms import PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from config import Config
from flask_app import login
from flask_app.auth import bp


def cookie_login_required(route_function):
    @wraps(route_function)
    def decorated_route(*args, **kwargs):
        if current_user.is_authenticated:
            return route_function(*args, **kwargs)
        user = User.check_token(request.cookies.get("token"))
        if user:
            login_user(user=user)
            return route_function(*args, **kwargs)
        return current_app.login_manager.unauthorized()

    return decorated_route


class User(FirestoreDocument, UserMixin):

    def __init__(self):
        super().__init__()
        self.email: str = str()
        self.password_hash: str = str()
        self.token: str = str()
        self.token_expiration: dt.datetime = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def check_token(cls, token) -> Optional["User"]:
        if not token:
            return None
        user = cls.objects.filter_by(token=token).first()
        if user is None or user.token_expiration < dt.datetime.utcnow().replace(tzinfo=pytz.UTC):
            return None
        return user

    def get_token(self, expires_in=Config.TOKEN_EXPIRY) -> str:
        now = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)
        if self.token and self.token_expiration > now + dt.timedelta(seconds=60):
            return self.token
        self.token = b64encode(os.urandom(24)).decode()
        self.token_expiration = now + dt.timedelta(seconds=expires_in)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_expiration = dt.datetime.utcnow() - dt.timedelta(seconds=1)
        self.save()


User.init()


@login.user_loader
def load_user(user_id: str) -> User:
    return User.get_by_id(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for('legacy.home'))
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('base_form.html', title='Sign In', form=form)
    user = User.objects.filter_by(email=form.email.data).first()
    if not user or not user.check_password(form.password.data):
        flash(f"Invalid email or password.")
        return redirect(url_for('auth.login'))
    token = user.get_token()
    login_user(user=user)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('legacy.home')
    response: Response = make_response(redirect(next_page))
    response.set_cookie("token", token, max_age=Config.TOKEN_EXPIRY, secure=Config.CI_SECURITY, httponly=True,
                        samesite="Strict")
    return response


@bp.route('/logout')
def logout():
    current_user.revoke_token()
    logout_user()
    return redirect(url_for('auth.login'))
