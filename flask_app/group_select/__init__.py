from flask import Blueprint

bp = Blueprint("group_select", __name__)

from flask_app.group_select import routes
