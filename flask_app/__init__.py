from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from config import Config

za_app = Flask(__name__)
za_app.config.from_object(Config)
bootstrap = Bootstrap(za_app)
login = LoginManager(za_app)
login.login_view = 'login'

from flask_app.auth import bp as auth_bp

za_app.register_blueprint(auth_bp)

from flask_app.legacy import bp as legacy_bp

za_app.register_blueprint(legacy_bp)
