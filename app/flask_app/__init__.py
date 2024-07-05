from flask import Flask

from .models import DATABASE
from .routes import app_routes, log

SQLALCHEMY_DATABASE_URI = "sqlite:///db_sqlite.db"
TESTING = False


def initial_app():
    # Create and configure Flasks application
    APP = Flask(__name__)
    APP.config["DEBUG"] = False
    APP.config["TESTING"] = TESTING
    APP.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    APP.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    log.debug("Initialization FLask application %s", APP)
    log.debug("Flask config:\n%s\n", APP.config)
    DATABASE.init_app(app=APP)
    with APP.app_context():
        DATABASE.create_all()

    @APP.route("/hello")
    def hello() -> dict:
        flask_config_info = {}
        for cfg_key, value in APP.config.items():
            flask_config_info[cfg_key] = str(value)
        return {"APP": {"Name Flask APP": APP.name, "flask_config": flask_config_info}}

    APP.register_blueprint(app_routes)
    return APP
