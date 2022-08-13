import os
from dotenv import load_dotenv
from datetime import timedelta
from api.util.system import strtobool

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get("FLASK_ENV") == "development":
    load_dotenv("development.env")
else:
    load_dotenv("production.env")


class Config:
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret_key")

    # SQLAlchemy settings
    # SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_DATABASE_URI = \
        f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CORS settings
    CORS_SUPPORTS_CREDENTIALS = True
    # JWT settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=120)
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-TOKEN-ACCESS"
    JWT_REFRESH_CSRF_HEADER_NAME = "X-CSRF-TOKEN-REFRESH"
    # Cookie
    # This should be true on production!
    # But when I'm using Ionic apps they handle communication differently
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_SESSION_COOKIE = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True
    JWT_ERROR_MESSAGE_KEY = "message"

    # Boilerplate settings.
    RESET_PASSWORD_TOKEN_EXPIRES = timedelta(hours=24)

    # Flask mail settings
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT", 25)
    MAIL_USE_TLS = strtobool(os.environ.get("MAIL_USE_TLS", "0"))
    MAIL_USE_SSL = strtobool(os.environ.get("MAIL_USE_SSL", "0"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    COMPRESS_MIMETYPES = ["application/json"]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

    # Allow anonymous to look users.
    VIEW_USER_AS_ANONYMOUS = strtobool(
        os.environ.get("VIEW_USER_AS_ANONYMOUS", "0"))
    # Users allowed to view each other profile
    ALLOW_TO_VIEW_OTHER_USER = strtobool(
        os.environ.get("ALLOW_TO_VIEW_OTHER_USER", "0"))

    DEFAULT_TIMEZONE = os.environ.get("DEFAULT_TIMEZONE", "Europe/Budapest")
