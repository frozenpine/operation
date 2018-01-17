@echo off

SETLOCAL

cd /d %~dp0

SET LOG_FILE=run\controller.log
SET APP_NAME=server.py
SET CONTROLLER_APP=TaskManager\Controller\%APP_NAME%
SET CONTROLLER_PID=run\controller.pid
SET _PID=

IF NOT EXIST run md run

IF NOT EXIST settings.conf (
    CALL :_ERR Config file "settings.conf" not exist.
    exit /b 1
)

for /F "tokens=1,2 delims==" %%i in ('findstr "^[^#]" .\settings.conf') do (
    CALL :_LOG %%i=%%~j 1>NUL
    SET %%i=%%~j
)

SET _command=%~1
IF NOT DEFINED _command (
    :INTERACTIVE
    cls
    echo.
    echo **************************************************
    echo *                                                *
    echo *       1. Show [h]elp message                   *
    echo *       2. Show Controller [s]tatus              *
    echo *       3. Star[t] Controller service            *
    echo *       4. Sto[p] Controller service             *
    echo *       5. [Q]uit                                *
    echo *                                                *
    echo **************************************************
    echo.
    CHOICE /C 12345hstpq /N /M "Please input you choice:"
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
CHOICE /C yn /N /D y /T 5 /M "Return to main menu? Auto quit in 5 seconds (Y/n):"
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
        echo Starting Controller.
        start /MIN "Controller" python %CONTROLLER_APP%
        CALL :STATUS 1>NUL 2>NUL
        CALL :STATUS
        deactivate
    )
) ELSE (
    echo Controller[%_PID%] is already running. >&2
    exit /b 1
)
GOTO :EOF

:STOP
CALL :STATUS 1>NUL 2>NUL
IF ERRORLEVEL 1 (
    echo Controller is already stopped. >&2
    exit /b 1
) ELSE (
    echo Stopping Controller.
    taskkill /F /PID %_PID%
    :LOOP
    CALL :STATUS 1>NUL 2>NUL
    IF NOT ERRORLEVEL 1 ping -n 1 127.0.0.1 >NUL & GOTO :LOOP
    CALL :STATUS
)
GOTO :EOF

:STATUS
IF EXIST %CONTROLLER_PID% (
    for /F %%i in (%CONTROLLER_PID%) do (
        wmic process where processid=%%i get commandline 2>NUL | findstr %APP_NAME% 1>NUL 2>NUL
        IF ERRORLEVEL 1 (
            SET _PID=
            CALL :_ERR Pid file exist, but controller not running, clean pid file.
            del /s/q %CONTROLLER_PID% 1>NUL 2>NUL
        ) ELSE (
            SET _PID=%%i
        )
    )
)
IF NOT DEFINED _PID (
    for /F "tokens=3 delims=," %%i in ('wmic process where name^=^"python.exe^" get processid^,commandline /FORMAT:CSV 2^>NUL ^| findstr %APP_NAME%') do (
        SET _PID=%%i
        IF DEFINED _PID (
            CALL :_LOG Controller running, but pid file missing, rebuild pid file.
            SET /p=%%i<NUL>%CONTROLLER_PID%
        )
    )
)
IF DEFINED _PID (
    echo Controller[%_PID%] is running.
    echo.
) ELSE (
    echo Controller is not running. >&2
    echo.
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
