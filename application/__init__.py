import os
import logging.config
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import connexion
from flask_marshmallow import Marshmallow
from application.exceptions import MissingEnvironmentValueException

with open("./application/logging.json") as config_data:
    json_config = json.load(config_data)
logging.config.dictConfig(json_config)

db = SQLAlchemy()
ma = Marshmallow()


def create_app(config=None):
    # Create the application instance
    _app = connexion.App(__name__, specification_dir='./')
    if config is None:
        #    _app.app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://bm_apps:1grogme2@localhost/machine_info_test"
        _app.app.config["SQLALCHEMY_DATABASE_URI"] = _get_db_uri()
        _app.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    else:
        for k, v in config:
            _app.app.config[k] = v

    db.init_app(_app.app)
    ma.init_app(_app.app)
    CORS(_app.app)

    with _app.app.app_context():
        # Build the SQLAlchemy models
        from . import models

        # Read the swagger.yml file to configure the endpoints
        _app.add_api('swagger.yml')

        return _app


def _get_db_uri():
    try:
        uri = os.environ["DB_URI"]
    except KeyError:
        raise MissingEnvironmentValueException("Environment does not define DB_URI")

    try:
        uname = os.environ["DB_USER_NAME"]
    except KeyError:
        raise MissingEnvironmentValueException("Environment does not define DB_USER_NAME")

    try:
        pwd = os.environ["DB_PASSWORD"]
    except KeyError:
        raise MissingEnvironmentValueException("Environment does not define DB_PASSWORD")

    try:
        host = os.environ["DB_HOST"]
    except KeyError:
        raise MissingEnvironmentValueException("Environment does not define DB_HOST")

    return uri.format(uname, pwd, host)
