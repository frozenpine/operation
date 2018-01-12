@echo off

cd /d %~dp0

SET INIT_APP=init.py

IF NOT EXIST settings.conf (
    echo Config file "settings.conf" not exist. >&2
    exit 1
)

for /F "tokens=1,2 delims==" %%i in ('findstr "^[^#]" .\settings.conf') do (
    SET %%i=%%~j
)

IF EXIST %VIRTUALENV%\Scripts\activate (
    CALL %VIRTUALENV%\Scripts\activate
) ELSE (
    echo Virtual enviroment not exist. >&2
    exit 1
)

python %INIT_APP% drop_db || (
    echo Faild to clean db. >&2
    exit 1
)
python %INIT_APP% create_db || (
    echo Faild to create db tables. >&2
    exit 1
)
python %INIT_APP% init_auth || (
    echo Faild to init auth info. >&2
    exit 1
)
python %INIT_APP% init_operation || (
    echo Faild to init operation catalog. >&2
    exit 1
)
