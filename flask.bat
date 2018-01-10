@echo off

cd /d %~dp0

set LOG_FILE=run\flask.log
set FLASK_APP=run.py
set FLASK_PID=run\flask.pid
set _PID=

if not exist run md run

if not exist settings.conf (
    call:_ERR settings.conf not exist.
    exit /b 1
)

for /F "tokens=1,2 delims==" %%i in (settings.conf) do (
    call:_LOG %%i=%%~j 1>nul
    set %%i=%%~j
)

if exist %VIRTUALENV%\Scripts\activate (
    call %VIRTUALENV%\Scripts\activate
) else (
    call:_ERR Virtual enviroment not exist.
    exit /b 1
)

set _command=%~1
if not defined _command (
    call:_HELP >&2
    exit /b 1
) else (
    echo %_command% | findstr /i /r "start stop status restart" 1>nul 2>nul
    if ERRORLEVEL 1 (
        call:_HELP >&2
        exit /b 1
    ) else (
        call:%_command%
    )
)

deactivate
GOTO:EOF

:START
call:STATUS 1>nul 2>nul
if ERRORLEVEL 1 (
    start /MIN "Flask" python %FLASK_APP% production
    call:STATUS 1>nul 2>nul
) else (
    echo Flask[%_PID%] is already running. >&2
    exit /b 1
)
GOTO:EOF

:STOP
call:STATUS 1>nul 2>nul
if ERRORLEVEL 1 (
    echo Flask is not running. >&2
    exit /b 1
) else (
    taskkill /F /PID %_PID%
    del /s/q %FLASK_PID% 1>nul 2>nul
)
GOTO:EOF

:STATUS
if exist %FLASK_PID% (
    for /F %%i in (%FLASK_PID%) do (
        wmic process where processid="%%i" get commandline | findstr %FLASK_APP% 1>nul 2>nul
        if ERRORLEVEL 1 (
            set _PID=
            call:_ERR Pid file exist, but process not running, clean pid file.
            del /s/q %FLASK_PID% 1>nul 2>nul
        ) else (
            set _PID=%%i
        )
    )
)
if not defined _PID (
    for /F "tokens=3 delims=," %%i in ('wmic process where name^=^"python.exe^" get processid^,commandline /FORMAT:CSV^|findstr %FLASK_APP%') do (
        set _PID=%%i
        if defined _PID (
            call:_LOG Process running, but pid file missing, rebuild pid file.
            set /p=%%i<nul>%FLASK_PID%
        )
    )
)
if defined _PID (
    echo Flask[%_PID%] is running.
) else (
    echo Flask is not running. >&2
    exit /b 1
)
GOTO:EOF

:RESTART
call:STOP
call:START
GOTO:EOF

:_ERR
echo %date% %time% [ERROR] %* >> %LOG_FILE%
echo [ERROR] %* >&2
GOTO:EOF

:_LOG
echo %date% %time% [INFO ] %* >> %LOG_FILE%
echo [INFO] %*
GOTO:EOF

:_HELP
echo Usage: %~nx0 ^[start^|stop^|status^|restart^]
GOTO:EOF
