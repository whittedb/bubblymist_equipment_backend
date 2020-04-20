@echo off
set DB_URI=mysql+pymysql://{}:{}@{}/machine_info_test
set DB_HOST=localhost
set DB_USER_NAME=bm_apps
set DB_PASSWORD=1grogme2
pipenv run python app.py
exit
