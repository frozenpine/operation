#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/worker.log"
cd  ${BASE_DIR}

WORKER_APP="TaskManager/Worker/worker.py"
WORKER_PID="run/worker.pid"
TM_USER="${UID}"
_WORKER_PID=

_ERR(){
    if [[ $# > 0 ]]; then
        echo "[ERROR] $*" >&2
        echo "`date '+%Y-%m-%d %H:%M:%S.%Z'` [ERROR] $*" >>"${LOG_FILE}"
    else
        echo "[ERROR]:"
        echo "`date '+%Y-%m-%d %H:%M:%S.%Z'` [ERROR]:" >>"${LOG_FILE}"
        cat >&2
        cat >>"${LOG_FILE}"
    fi
}

_LOG(){
    if [[ $# > 0 ]]; then
        echo "[INFO] $*"
    else
        echo "[INFO]:"
        cat
    fi
}

if [[ ! -d "${BASE_DIR}/run" ]]; then
    mkdir -p "${BASE_DIR}/run"
fi

[[ -s "${BASE_DIR}/settings.conf" ]] && {
    source "${BASE_DIR}/settings.conf"
    sed 's/^\([^#]*\)#.*$/\1/g; /^ *$/d' settings.conf | awk -F'=' '{print $1}' | while read VARIABLE; do
        eval "export $VARIABLE"
    done
} || {
    _ERR '"settings.conf" not found!'
    exit 1
}

worker_status(){
    if [[ -f "${WORKER_PID}" ]]; then
        _WORKER_PID=`cat "${WORKER_PID}"`
        kill -0 ${_WORKER_PID} &>/dev/null
        if [[ $? == 0 ]]; then
            ps -fu ${TM_USER} | awk '$2=='${_WORKER_PID}' && $0 ~/'"`basename ${WORKER_APP}`"'/{print}' | grep python &>/dev/null
            if [[ $? == 0 ]]; then
                _LOG "Worker[${_WORKER_PID}] is running."
                echo
                return 0
            fi
        fi
        _WORKER_PID=
        _ERR "Incorrect pid file, clean pid file."
        echo
        rm -f "${WORKER_PID}"
    fi
    _WORKER_PID=`ps -fu "${TM_USER}" | grep "${WORKER_APP}" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_WORKER_PID} ]]; then
        _LOG "Worker[${_WORKER_PID}] is running."
        echo
        echo -n ${_WORKER_PID}>"${WORKER_PID}"
        return 0
    else
        _LOG "Worker not running."
        echo
        return 1
    fi
}

worker_start(){
    worker_status &>/dev/null
    if [[ $? == 0 ]]; then
        echo
        _ERR "Worker[${_WORKER_PID}] is already running."
        echo
        return 1
    else
        # switch to python virtual env
        source "${BASE_DIR}/${VIRTUALENV}/bin/activate"
        echo
        _LOG "Starting Worker"
        nohup python "${WORKER_APP}" &>"${BASE_DIR}/run/worker.out" &
        _WORKER_PID=$!
        echo -n ${_WORKER_PID} >"${WORKER_PID}"
        worker_status
    fi
}

worker_stop(){
    worker_status &>/dev/null
    if [[ $? == 0 ]]; then
        echo
        _LOG "Stopping Worker."
        kill ${_WORKER_PID} &>/dev/null
        while true; do
            worker_status &>/dev/null
            if [[ $? == 0 ]]; then
                kill -9 ${_WORKER_PID} &>/dev/null
                sleep 1
            else
                break
            fi
        done
        worker_status
    else
        echo
        _ERR "Worker already stopped."
        echo
        return 1
    fi
}

case $1 in
    'start')
        worker_start || exit 1
    ;;
    'stop')
        worker_stop || exit 1
    ;;
    'status')
        echo
        worker_status || exit 1
    ;;
    'restart')
        worker_stop
        worker_start || exit 1
    ;;
    *)
        echo "Usage: `basename $0` [start|stop|status|restart]" >&2
        exit 1
    ;;
esac
