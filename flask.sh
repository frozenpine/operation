#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/flask.log"
cd ${BASE_DIR}

FLASK_APP="run.py"
FLASK_MODE="production"
FLASK_PID="run/flask.pid"
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
        if [[ $? == 0 ]]; then
            ps -fu ${FLASK_USER} | awk '$2=='${_PID}' && $0 ~/'"${FLASK_APP} ${FLASK_MODE}"'/{print}' | grep python &>/dev/null
            if [[ $? == 0 ]]; then
                _LOG "Flask[${_PID}] is running."
                echo
                return 0
            fi
            _PID=
            _ERR "Incorrect pid file, clean pid file."
            echo
            rm -f "${FLASK_PID}"
        fi
    fi
    _PID=`ps -fu "${FLASK_USER}" | grep "${FLASK_APP} ${FLASK_MODE}" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_PID} ]]; then
        _LOG "Flask[${_PID}] is running, rebuild pid file."
        echo
        echo -n ${_PID}>"${FLASK_PID}"
        return 0
    else
        _LOG "Flask not running."
        echo
        return 1
    fi
}

flask_start(){
    flask_status &>/dev/null
    if [[ $? == 0 ]]; then
        echo
        _ERR "Flask[${_PID}] is already running."
        echo 
        return 1
    else
        # switch to python virtual env
        source "${BASE_DIR}/${VIRTUALENV}/bin/activate"
        echo
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
        echo
        _LOG "Stopping Flask."
        kill ${_PID} &>/dev/null
        while true; do
            flask_status &>/dev/null
            if [[ $? == 0 ]]; then
                kill -9 ${_PID} &>/dev/null
                sleep 1
            else
                break
            fi
        done
        flask_status
    else
        echo
        _ERR "Flask already stopped."
        echo
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
        echo
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
