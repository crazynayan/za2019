import os
from base64 import b64encode


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or b64encode(os.urandom(24)).decode()
    CI_SECURITY = False
    SESSION_COOKIE_SECURE = CI_SECURITY
    TOKEN_EXPIRY = 3600  # 1 hour = 3600 seconds
    IMAGES = set(os.listdir('flask_app/static/images'))
    EXT = {'.jpg', '.jpeg', '.png'}
