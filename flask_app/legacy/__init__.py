from flask import Blueprint

bp = Blueprint("legacy", __name__)

from flask_app.legacy import routes
