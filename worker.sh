#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/worker.log"
cd  ${BASE_DIR}

WORKER_APP="${BASE_DIR}/TaskManager/Worker/worker.py"
WORKER_PID="${BASE_DIR}/run/worker.pid"
TM_USER="${UID}"
_WORKER_PID=

#source "${BASE_DIR}/settings.conf"

if [[ ! -d "${BASE_DIR}/run" ]]; then
    mkdir -p "${BASE_DIR}/run"
fi

# switch to python virtual env
source "${BASE_DIR}/bin/activate"
# export FLASK_HOST
# export FLASK_PORT
# export TM_HOST
# export TM_PORT

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

worker_status(){
    if [[ -f "${WORKER_PID}" ]]; then
        _WORKER_PID=`cat "${WORKER_PID}"`
        kill -0 ${_WORKER_PID} &>/dev/null
        if [[ $? == 0 ]]; then
            _LOG "Worker is running[${_WORKER_PID}]."
            return 0
        else
            _WORKER_PID=
            _ERR "Worker pid file is incorrect, cleaned."
            rm -f "${WORKER_PID}"
        fi
    fi
    _WORKER_PID=`ps -fu "${TM_USER}" | grep "python TaskManager/Worker/worker.py" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_WORKER_PID} ]]; then
        _LOG "Worker is running[${_WORKER_PID}]."
        echo -n ${_WORKER_PID}>"${WORKER_PID}"
        return 0
    else
        _ERR "Worker not running."
        return 1
    fi
}

worker_start(){
    worker_status &>/dev/null
    if [[ $? == 0 ]]; then
        _ERR "Worker already running[${_WORKER_PID}]"
        exit 1
    else
        nohup python "${WORKER_APP}" &>"${BASE_DIR}/run/worker.out" &
        _WORKER_PID=$!
        echo -n ${_WORKER_PID} >"${WORKER_PID}"
        _LOG "Worker started[PID:${_WORKER_PID}]"
    fi
}

worker_stop(){
    worker_status &>/dev/null
    if [[ $? == 0 ]]; then
        kill ${_WORKER_PID} &>/dev/null && kill -9 ${_WORKER_PID} &>/dev/null
        _LOG "Worker stopped[PID:${_WORKER_PID}]."
        rm -f "${WORKER_PID}"
    else
        _ERR "Worker already stopped."
        exit 1
    fi
}

case $1 in
    'start')
        worker_start
    ;;
    'stop')
        worker_stop
    ;;
    'status')
        worker_status
    ;;
    'restart')
        worker_stop
        sleep 3
        worker_start
    ;;
    *)
        echo "Usage: `basename $0` [start|stop|status|restart]" >&2
        exit 1
    ;;
esac
