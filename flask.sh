#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/flask.log"
cd  ${BASE_DIR}

FLASK_APP="${BASE_DIR}/run.py"
FLASK_PID="${BASE_DIR}/run/flask.pid"
FLASK_USER="devops"
_PID=

# switch to python virtual env
source "${BASE_DIR}/bin/activate"

_ERR(){
    if [[ $# > 0 ]]; then
        echo "[ERROR] $*" >&2
        echo "`date '+%Y-%m-%d %H:%M:%S.%N'` [ERROR] $*" >>"${LOG_FILE}"
    else
        echo "[ERROR]:"
        echo "`date '+%Y-%m-%d %H:%M:%S.%N'` [ERROR]:" >>"${LOG_FILE}"
        cat >&2
        cat >>"${LOG_FILE}"
    fi
}

_LOG(){
    if [[ $# > 0 ]]; then
        echo "[INFO] $*"
        echo "`date '+%Y-%m-%d %H:%M:%S.%N'` [INFO] $*" >>"${LOG_FILE}"
    else
        echo "[INFO]:"
        echo "`date '+%Y-%m-%d %H:%M:%S.%N'` [INFO]:" >>"${LOG_FILE}"
        cat
        cat >>"${LOG_FILE}"
    fi
}

flask_status(){
    if [[ -f "${FLASK_PID}" ]]; then
        _PID=`cat "${FLASK_PID}"`
        kill -0 ${_PID} &>/dev/null
        if [[ $? == 0 ]]; then
            _LOG "Flask is running[${_PID}]."
            return 0
        else
            _PID=
            _ERR "Flask pid file is incorrect, cleaned."
            rm -f "${FLASK_PID}"
        fi
    fi
    _PID=`ps -fu "${FLASK_USER}" | grep "python run.py production" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_PID} ]]; then
        _LOG "Flask is running[${_PID}]."
        echo -n ${_PID}>"${FLASK_PID}"
        return 0
    else
        _ERR "Flask not running."
        return 1
    fi
}

flask_start(){
    flask_status &>/dev/null
    if [[ $? == 0 ]]; then
        _ERR "Flask already running[${_PID}]"
        exit 1
    else
        nohup python "${FLASK_APP}" production &>"${BASE_DIR}/run/flask.out" &
        _PID=$!
        echo -n ${_PID} >"${FLASK_PID}"
        _LOG "Flask started[PID:${_PID}]"
    fi
}

flask_stop(){
    flask_status &>/dev/null
    if [[ $? == 0 ]]; then
        kill ${_PID} &>/dev/null
        flask_status
        if [[ $? != 0 ]]; then
            kill -9 ${_PID} &>/dev/null
            sleep 1
        fi
        _LOG "Flask stopped[PID:${_PID}]."
        rm -f "${FLASK_PID}"
    else
        _ERR "Flask already stopped."
        exit 1
    fi
}

case $1 in
    'start')
        flask_start
    ;;
    'stop')
        flask_stop
    ;;
    'status')
        flask_status
    ;;
    'restart')
        flask_stop
        sleep 3
        flask_start
    ;;
    *)
        echo "Usage: `basename $0` [start|stop|status|restart]" >&2
        exit 1
    ;;
esac
