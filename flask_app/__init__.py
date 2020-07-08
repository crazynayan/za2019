from flask import Flask, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf import FlaskForm

from config import Config

za_app = Flask(__name__)
za_app.config.from_object(Config)
bootstrap = Bootstrap(za_app)
login = LoginManager(za_app)
login.login_view = 'auth.login'


class FSForm(FlaskForm):
    def flash_form_errors(self) -> None:
        for _, errors in self.errors.items():
            for error in errors:
                if error:
                    flash(error)
        return


from flask_app.auth import bp as auth_bp

za_app.register_blueprint(auth_bp)

from flask_app.legacy import bp as legacy_bp

za_app.register_blueprint(legacy_bp)

from flask_app.group_select import bp as select_bp

za_app.register_blueprint(select_bp)
