from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from config import Config

za_app = Flask(__name__)
za_app.config.from_object(Config)
bootstrap = Bootstrap(za_app)
login = LoginManager(za_app)
login.login_view = 'login'

# noinspection PyPep8
from flask_app import routes, auth
