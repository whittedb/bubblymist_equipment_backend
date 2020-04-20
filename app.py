import os
import json
import logging.config
from db import db
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import connexion
from exceptions import MissingEnvironmentValueException


with open("logging.json") as config_data:
    json_config = json.load(config_data)
logging.config.dictConfig(json_config)

ma = Marshmallow()


def create_app():
    # Create the application instance
    _app = connexion.App(__name__, specification_dir='./')
    db_uri = _get_db_uri()
#    _app.app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://bm_apps:1grogme2@localhost/machine_info_test"
    _app.app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    _app.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(_app.app)
    ma.init_app(_app.app)
    CORS(_app.app)
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


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app = create_app()
    app.run()
