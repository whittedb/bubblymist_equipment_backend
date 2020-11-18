import logging
from application.app_logging import logger
from application import create_app


if __name__ != "__main__":
    # Production mode via gunicorn
    gunicorn_logger = logging.getLogger("gunicorn.error")
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)

app = create_app()

if __name__ == "__main__":
    app.run()
