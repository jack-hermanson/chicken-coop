from __future__ import annotations

import sys
from logging.handlers import TimedRotatingFileHandler

from flask_bcrypt import Bcrypt
from flask import Flask, abort

from main.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
import os

from datetime import date, datetime
from logger import StreamLogFormatter, FileLogFormatter

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate(compare_type=True)
logging.basicConfig(level=logging.DEBUG)

login_manager = LoginManager()
login_manager.login_view = "accounts.login"
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    # set up file paths for static resources
    app = Flask(
        __name__,
        static_url_path="/static",
        static_folder="web/static",
        template_folder="web/templates"
    )

    # set up environment variables
    app.config.from_object(config_class)

    # set up https / security
    # Talisman(
    #     app,
    #     content_security_policy=None
    # )

    # bcrypt
    bcrypt.init_app(app)

    # models
    from .modules.people import models
    from .modules.shifts import models
    from .modules.accounts import models

    # database
    db.app = app
    db.init_app(app)
    # looks like we don't need create_all() because we are doing migrations
    # with app.app_context():
    #     db.create_all()
    migrate.init_app(app, db)

    # routes and blueprints
    from .modules.main.routes import main
    from .modules.admin.routes import admin
    from .modules.accounts.routes import accounts
    from .modules.shifts.routes import shifts

    for blueprint in [main, accounts, admin, shifts]:
        app.register_blueprint(blueprint)

    login_manager.init_app(app)

    # middleware
    # @app.before_request
    # def request_middleware():
    #     pass

    # filter
    @app.template_filter()
    def day_of_week_str(raw):
        from utils import date_functions
        return date_functions.day_of_week_str(raw)

    @app.template_filter()
    def time_of_day_str(raw):
        from utils import date_functions
        return date_functions.time_of_day_str(raw)

    @app.template_filter()
    def extract_date(date_or_datetime: date | datetime):
        from utils import date_functions
        return date_functions.extract_date(date_or_datetime)

    @app.template_filter()
    def number_suffix(value):
        if 10 <= value % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
        return f"{value}{suffix}"

    # return the app
    print("RUNNING APPLICATION")
    logger.debug("LOGGING IS RUNNING")
    logger.info(f"Running app in environment '{os.environ.get('ENVIRONMENT')}'")
    logger.info(f"FLASK_ENV: '{os.environ.get('FLASK_ENV')}'")
    return app


# Set up logging
# Set up logging
logging.basicConfig()
logger = logging.getLogger("chicken-coop")
logger.propagate = False
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(StreamLogFormatter())

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

fh = TimedRotatingFileHandler(os.path.join(log_dir, "logs.txt"), when="midnight", interval=1, backupCount=7)
fh.setFormatter(FileLogFormatter())
fh.suffix += ".txt"
fh.namer = lambda name: name.replace(".txt", "") + ".txt"

logger.addHandler(fh)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG if (
        os.environ.get("FLASK_ENV") == "dev" or os.environ.get("FLASK_ENV") == "development") else logging.INFO)
