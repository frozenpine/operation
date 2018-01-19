@echo off

SETLOCAL

cd /d %~dp0

SET INIT_APP=init.py

IF NOT EXIST settings.conf (
    echo Config file "settings.conf" not exist. >&2
    exit 1
)

for /F "tokens=1,2,* delims==" %%i in ('findstr "^[^#]" .\settings.conf') do (
    echo %%i=%%~j%%~k
    IF "%%k" == "" (
        SET %%i=%%~j
    ) ELSE (
        SET %%i=^"%%~j^=%%k
    )
)
IF DEFINED FLASK_SQLALCHEMY_DATABASE_URI (
    SET FLASK_SQLALCHEMY_DATABASE_URI=%FLASK_SQLALCHEMY_DATABASE_URI:"=%
)

SET _COMMAND=%~1
IF EXIST %VIRTUALENV%\Scripts\activate (
    CALL %VIRTUALENV%\Scripts\activate
    IF DEFINED _COMMAND (
        CALL :%_COMMAND%
    ) ELSE (
        CALL :DB && (
            CALL :AUTH
            CALL :INVENTORY
            CALL :OPERATION
        )
    )
) ELSE (
    echo Virtual enviroment not exist. >&2
    exit 1
)
GOTO :EOF

:DB
python %INIT_APP% drop_db || (
    echo Faild to clean db. >&2
    exit /B 1
)
IF ERRORLEVEL 0 python %INIT_APP% create_db || (
    echo Faild to create db tables. >&2
    exit /B 1
)
GOTO :EOF

:AUTH
python %INIT_APP% init_auth || (
    echo Faild to init auth info. >&2
    exit /B 1
)
GOTO :EOF

:INVENTORY
python %INIT_APP% init_inventory || (
    echo Faild to init inventory info. >&2
    exit 1
)
GOTO :EOF

:OPERATION
python %INIT_APP% init_operation || (
    echo Faild to init operation catalog. >&2
    exit 1
)
GOTO :EOF
