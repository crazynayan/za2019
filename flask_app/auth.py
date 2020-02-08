from firestore_ci import FirestoreDocument
from flask import flash, redirect, url_for, render_template, request
from flask_login import UserMixin, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from wtforms import PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from flask_app import login, za_app


class User(FirestoreDocument, UserMixin):

    def __init__(self):
        super().__init__()
        self.email: str = str()
        self.password_hash: str = str()

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


User.init()


@login.user_loader
def load_user(user_id: str) -> User:
    return User.get_by_id(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


@za_app.route('/login', methods=['GET', 'POST'])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('base_form.html', title='Sign In', form=form)
    user = User.objects.filter_by(email=form.email.data).first()
    if not user or not user.check_password(form.password.data):
        flash(f"Invalid email or password.")
        return redirect(url_for('login'))
    login_user(user=user)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('home')
    return redirect(next_page)


@za_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
