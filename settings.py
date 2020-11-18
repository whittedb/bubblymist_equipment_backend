import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_URI = os.environ.get("DB_URI")
DB_HOST = os.environ.get("DB_HOST")
DB_USER_NAME = os.environ.get("DB_USER_NAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
MASTER_KEY = os.environ.get("MASTER_KEY")
LOG_DATE_FMT = os.environ.get("LOG_DATE_FMT", "%Y%m%d %H:%M:%S")
LOG_FMT = os.environ.get("LOG_FMT", "%(asctime)s:%(levelname)s:%(threadName)-9s:%(module)s.%(funcName)s - %(message)s")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
APP_NAME = "bm_equipment"
