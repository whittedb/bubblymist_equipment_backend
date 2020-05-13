import os
import logging.config
from logging import INFO, DEBUG
import json
from application import create_app

# Set up logging
with open("./application/logging.json") as config_data:
    json_config = json.load(config_data)
logging.config.dictConfig(json_config)

_logger = logging.getLogger()
if __name__ == "__main__":
    # Development mode
    _log_level = os.environ.get("LOG_LEVEL", "DEBUG")
    _log_level_name = logging.getLevelName(_log_level)
    if _log_level_name is None:
        _logger.setLevel(INFO)
    elif isinstance(_log_level_name, str):
        _logger.warning("Specified log level unrecognized: {}".format(_log_level_name))
        _logger.setLevel(INFO)
    else:
        _logger.setLevel(_log_level_name)
else:
    # Production mode via gunicorn
    gunicorn_logger = logging.getLogger("gunicorn.error")
    _logger.handlers = gunicorn_logger.handlers
    _logger.setLevel(gunicorn_logger.level)

app = create_app()

if __name__ == "__main__":
    app.run()
