@echo off

cd /d %~dp0

SET LOG_FILE=run\flask.log
SET FLASK_APP=run.py
SET FLASK_MODE=production
SET FLASK_PID=run\flask.pid
SET _PID=

IF NOT EXIST run md run

IF NOT EXIST settings.conf (
    CALL :_ERR Config file "settings.conf" not exist.
    exit /b 1
)

for /F "tokens=1,2 delims==" %%i in (settings.conf) do (
    CALL :_LOG %%i=%%~j 1>NUL
    SET %%i=%%~j
)

SET _command=%~1
IF NOT DEFINED _command (
    :INTERACTIVE
    clear
    echo.
    echo **************************************************
    echo *                                                *
    echo *          1. Show [h]elp message                *
    echo *          2. Show Flask [s]tatus                *
    echo *          3. Star[t] Flask service              *
    echo *          4. Sto[p] Flask service               *
    echo *          5. [Q]uit                             *
    echo *                                                *
    echo *   Default choice [2] in 5 seconds delay.       *
    echo *                                                *
    echo **************************************************
    echo.
    CHOICE /C 12345hstpq /T 5 /D 2 /N /M "Please input you choice:"
    IF ERRORLEVEL 10 GOTO :EOF
    IF ERRORLEVEL 9 (
        echo.
        CALL :STOP
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
    IF ERRORLEVEL 8 (
        echo.
        CALL :START
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
    IF ERRORLEVEL 7 (
        echo.
        CALL :STATUS
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
    IF ERRORLEVEL 6 (
        echo.
        CALL :HELP
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
    IF ERRORLEVEL 5 GOTO :EOF
    IF ERRORLEVEL 4 (
        echo.
        CALL :STOP
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
    IF ERRORLEVEL 3 (
        echo.
        CALL :START
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
    IF ERRORLEVEL 2 (
        echo.
        CALL :STATUS
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
    IF ERRORLEVEL 1 (
        echo.
        CALL :HELP
        echo.
        CALL :ASK
        IF ERRORLEVEL 2 GOTO :EOF
        IF ERRORLEVEL 1 GOTO :INTERACTIVE
    )
) ELSE (
    echo %_command% | findstr /i /r "start stop status restart help" 1>NUL 2>NUL
    IF ERRORLEVEL 1 (
        echo.
        CALL :HELP >&2
        exit /b 1
    ) ELSE (
        echo.
        CALL :%_command%
    )
)
GOTO :EOF

:ASK
CHOICE /C yn /N /D n /T 5 /M "Return to main menu? Auto quit in 5 seconds (y/N):"
GOTO :EOF

:ACTIVATE
IF EXIST %VIRTUALENV%\Scripts\activate (
    CALL %VIRTUALENV%\Scripts\activate
) ELSE (
    CALL :_ERR Virtual enviroment not exist.
    exit /b 1
)
GOTO :EOF

:START
CALL :STATUS 1>NUL 2>NUL
IF ERRORLEVEL 1 (
    CALL :ACTIVATE
    IF ERRORLEVEL 0 (
        echo Starting Flask.
        start /MIN "Flask" python %FLASK_APP% %FLASK_MODE%
        CALL :STATUS 1>NUL 2>NUL
        CALL :STATUS
        deactivate
    )
) ELSE (
    echo Flask[%_PID%] is already running. >&2
    exit /b 1
)
GOTO :EOF

:STOP
CALL :STATUS 1>NUL 2>NUL
IF ERRORLEVEL 1 (
    echo Flask is already stopped. >&2
    exit /b 1
) ELSE (
    echo Stopping Flask.
    taskkill /F /PID %_PID%
    :LOOP
    CALL :STATUS 1>NUL 2>NUL
    IF NOT ERRORLEVEL 1 ping -n 1 127.0.0.1 >NUL & GOTO :LOOP
    CALL :STATUS
)
GOTO :EOF

:STATUS
IF EXIST %FLASK_PID% (
    for /F %%i in (%FLASK_PID%) do (
        wmic process where processid=%%i get commandline 2>NUL | findstr %FLASK_APP% 1>NUL 2>NUL
        IF ERRORLEVEL 1 (
            SET _PID=
            CALL :_ERR Pid file exist, but flask not running, clean pid file.
            del /s/q %FLASK_PID% 1>NUL 2>NUL
        ) ELSE (
            SET _PID=%%i
        )
    )
)
IF NOT DEFINED _PID (
    for /F "tokens=3 delims=," %%i in ('wmic process where name^=^"python.exe^" get processid^,commandline /FORMAT:CSV 2^>NUL ^| findstr %FLASK_APP%') do (
        SET _PID=%%i
        IF DEFINED _PID (
            CALL :_LOG Flask running, but pid file missing, rebuild pid file.
            SET /p=%%i<NUL>%FLASK_PID%
        )
    )
)
IF DEFINED _PID (
    echo Flask[%_PID%] is running.
) ELSE (
    echo Flask is not running. >&2
    exit /b 1
)
GOTO :EOF

:RESTART
CALL :STOP
CALL :START
GOTO :EOF

:_ERR
echo %date% %time% [ERROR] %* >> %LOG_FILE%
echo [ERROR] %* >&2
GOTO :EOF

:_LOG
echo %date% %time% [INFO ] %* >> %LOG_FILE%
echo [INFO] %*
GOTO :EOF

:HELP
echo Usage: %~nx0 ^[start^|stop^|status^|restart^|help^]
GOTO :EOF
