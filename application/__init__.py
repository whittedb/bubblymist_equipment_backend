import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import connexion
from .exceptions import MissingEnvironmentValueException
from .app_logging import logger
import settings as settings

db = SQLAlchemy()
ma = Marshmallow()


def create_app(config=None):
    logger.info("Starting %s" % settings.APP_NAME)

    # Create the application instance
    _app = connexion.App(__name__, specification_dir='./')
    _app.app.secret_key = b'21\x08\xa8\x84\x16\xcd\xb0[\xedL\xa5b\x04J,'

    if config is None:
        #    _app.app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://bm_apps:1grogme2@localhost/machine_info_test"
        _app.app.config["SQLALCHEMY_DATABASE_URI"] = _get_db_uri()
        _app.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    else:
        for k, v in config:
            _app.app.config[k] = v

    db.init_app(_app.app)
    ma.init_app(_app.app)
    if os.environ.get("ENV", "development") == "development":
        CORS(_app.app, origins="*", supports_credentials=True)
    else:
        CORS(_app.app)

    with _app.app.app_context():
        # Build the SQLAlchemy models
        from . import models

        # Read the swagger.yml file to configure the endpoints
        _app.add_api('swagger.yml')

        return _app


def _get_db_uri():
    if settings.DB_URI:
        uri = os.environ["DB_URI"]
    else:
        raise MissingEnvironmentValueException("Environment does not define DB_URI")

    if settings.DB_USER_NAME:
        uname = os.environ["DB_USER_NAME"]
    else:
        raise MissingEnvironmentValueException("Environment does not define DB_USER_NAME")

    if settings.DB_PASSWORD:
        pwd = os.environ["DB_PASSWORD"]
    else:
        raise MissingEnvironmentValueException("Environment does not define DB_PASSWORD")

    if settings.DB_HOST:
        host = os.environ["DB_HOST"]
    else:
        raise MissingEnvironmentValueException("Environment does not define DB_HOST")

    return uri.format(uname, pwd, host)
