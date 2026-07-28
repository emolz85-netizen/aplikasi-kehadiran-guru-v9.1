@echo off
cd /d "%~dp0"
if not exist .env copy .env.example .env >nul
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed_users
start "" http://127.0.0.1:8000
py manage.py runserver 0.0.0.0:8000
pause
