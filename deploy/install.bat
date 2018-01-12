@echo off

cd /d %~dp0
SET LOG_FILE=install.log

SET _COMMAND=%~1
IF NOT DEFINED _COMMAND (
    IF EXIST VCForPython27.msi (
        CALL :_LOG Start to install VC 4 python
        start /w VCForPython27.msi
    ) ELSE (
        CALL :_ERR VC for python installation package missing.
        exit 1
    )

    IF EXIST python-2.7.13.amd64.msi (
        CALL :_LOG Start to install python 2.7.13
        start /w python-2.7.13.amd64.msi
    ) ELSE (
        CALL :_ERR Python installation package missing.
        exit 1
    )
    start %~0 makeenv
) ELSE (
    CALL :%_COMMAND%
)

GOTO :EOF

:MAKEENV
PUSHD ..\
IF NOT EXIST settings.conf (
    CALL :_ERR Config file "settings.conf" not exist.
    exit 1
)

for /F "tokens=1,2 delims==" %%i in ('findstr "^[^#]" .\settings.conf') do (
    CALL :_LOG %%i=%%~j 1>NUL
    SET %%i=%%~j
)
POPD

CALL :_LOG Starting to upgrade setuptools.
PUSHD requirements\setuptools-38.4.0
python setup.py install
POPD

CALL :_LOG Starting to install pip
PUSHD requirements\pip-9.0.1
python setup.py install
POPD

CALL :_LOG Starting to install virtualenv
PUSHD requirements\virtualenv-15.1.0
python setup.py install
POPD

CALL :_LOG Starting to build virtualenv
PUSHD ..\
python -m virtualenv .virtual
CALL :ACTIVATE
IF NOT ERRORLEVEL 1 (
    POPD
    CALL :_LOG Starting to install python requirements
    python -m pip install --no-index --find-links=requirements -r requirements.txt --no-cache-dir
    deactivate
    exit
)
GOTO :EOF

:ACTIVATE
IF EXIST %VIRTUALENV%\Scripts\activate (
    CALL %VIRTUALENV%\Scripts\activate
) ELSE (
    CALL :_ERR Virtual enviroment not exist.
    exit /b 1
)
GOTO :EOF

:_ERR
echo %date% %time% [ERROR] %* >> %LOG_FILE%
echo [ERROR] %* >&2
GOTO :EOF

:_LOG
echo %date% %time% [INFO ] %* >> %LOG_FILE%
echo [INFO] %*
GOTO :EOF
