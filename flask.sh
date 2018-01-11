#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/flask.log"
cd ${BASE_DIR}

FLASK_APP="${BASE_DIR}/run.py"
FLASK_MODE="production"
FLASK_PID="${BASE_DIR}/run/flask.pid"
FLASK_USER="${UID}"
_PID=

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

if [[ ! -d "${BASE_DIR}/run" ]]; then
    mkdir -p "${BASE_DIR}/run"
fi

[[ -s "${BASE_DIR}/settings.conf" ]] && source "${BASE_DIR}/settings.conf" || {
    _ERR '"settings.conf" not found!'
    exit 1
}

flask_status(){
    if [[ -f "${FLASK_PID}" ]]; then
        _PID=`cat "${FLASK_PID}"`
        kill -0 ${_PID} &>/dev/null
        if [[ $? eq 0 ]]; then
            ps -fu ${FLASK_USER} | awk '$2=='${_PID}' && $0 ~/python run.py/{print}' | grep python &>/dev/null
            if [[ $? eq 0 ]]; then
                _LOG "Flask[${_PID}] is running."
                return 0
            fi
            _PID=
            _ERR "Incorrect pid file, clean pid file."
            rm -f "${FLASK_PID}"
        fi
    fi
    _PID=`ps -fu "${FLASK_USER}" | grep "python run.py" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_PID} ]]; then
        _LOG "Flask[${_PID}] is running, rebuild pid file."
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
        _ERR "Flask[${_PID}] is already running."
        return 1
    else
        # switch to python virtual env
        source "${BASE_DIR}/${VIRTUALENV}/bin/activate"
        _LOG "Starting Flask."
        nohup python "${FLASK_APP}" ${FLASK_MODE} &>"${BASE_DIR}/run/flask.out" &
        _PID=$!
        echo -n ${_PID} >"${FLASK_PID}"
        flask_status
    fi
}

flask_stop(){
    flask_status &>/dev/null
    if [[ $? == 0 ]]; then
        _LOG "Stopping Flask."
        kill ${_PID} &>/dev/null
        while true; do
            flask_status &>/dev/null
            if [[ $? != 0 ]]; then
                kill -9 ${_PID} &>/dev/null
                sleep 1
            else
                break
            fi
        done
        flask_status
    else
        _ERR "Flask already stopped."
        return 1
    fi
}

case $1 in
    'start')
        flask_start || exit 1
    ;;
    'stop')
        flask_stop || exit 1
    ;;
    'status')
        flask_status || exit 1
    ;;
    'restart')
        flask_stop && flask_start || exit 1
    ;;
    *)
        echo "Usage: `basename $0` [start|stop|status|restart]" >&2
        exit 1
    ;;
esac
