@echo off
chcp 936

SETLOCAL
SET BASE_DIR=%~dp0
SET INSTALL_LOG=%BASE_DIR%\install.log
SET PY_VIRTUALENV_NAME="devops"

cd %BASE_DIR%

IF EXIST python-2.7.13.amd64.msi (
    echo Start to install python 2.7.13
    python-2.7.13.amd64.msi
) ELSE (
    echo Python installation package missing.
    exit /b 1
)

IF EXIST VCForPython27.msi (
    echo Start to install VC 4 python
    VCForPython27.msi
    SET PATH=%PATH%
) ELSE (
    echo VC for python installation package missing.
    exit /b 1
)

where pip
IF %ERRORLEVEL%==0 (
    echo Install virtualenv.
    for /r requirements %i in (pip-*.tar.gz) do SET PIP_FILE=%i
    pip install %PIP_FILE%
) ELSE (
    echo ""
)

ENDLOCAL
