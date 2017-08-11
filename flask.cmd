@echo off

BASE_DIR=%~dp0
LOG_FILE="%BASE_DIR%\run\flask.log"
cd "%BASE_DIR%"

FLASK_APP="%BASE_DIR%\run.py"

call "BASE_DIR\bin\activate"

call python "%FLASK_APP%" production &>"%LOG_FILE%"
