import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    TEMPLATES_AUTO_RELOAD = True
    environment = os.getenv("ENVIRONMENT")
    SECRET_KEY = os.getenv("SECRET_KEY")
    if os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
