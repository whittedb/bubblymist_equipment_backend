import json
import logging.config
import settings

# logging.basicConfig(format=settings.LOG_FMT, datefmt=settings.LOG_DATE_FMT)

with open("application/logging.json") as config_data:
    json_config = json.load(config_data)
logging.config.dictConfig(json_config)

logger = logging.getLogger(settings.APP_NAME)
logger.setLevel(settings.LOG_LEVEL)
