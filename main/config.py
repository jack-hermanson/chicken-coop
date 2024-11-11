import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    TEMPLATES_AUTO_RELOAD = True
    environment = os.getenv("ENVIRONMENT")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SECRET_CODE = os.getenv("SECRET_CODE")  # not the same as secret key - this is just the padlock code
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("EMAIL_FROM_ADDRESS")
    MAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False
    TESTING = False
