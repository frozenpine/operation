#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/Worker.log"
cd  ${BASE_DIR}

Worker_APP="${BASE_DIR}/Worker/Worker/Worker.py"
Worker_PID="${BASE_DIR}/run/Worker.pid"
TM_USER="${UID}"
_Worker_PID=

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
    if [[ -f "${Worker_PID}" ]]; then
        _Worker_PID=`cat "${Worker_PID}"`
        kill -0 ${_Worker_PID} &>/dev/null
        if [[ $? == 0 ]]; then
            _LOG "Worker is running[${_Worker_PID}]."
            return 0
        else
            _Worker_PID=
            _ERR "Worker pid file is incorrect, cleaned."
            rm -f "${Worker_PID}"
        fi
    fi
    _Worker_PID=`ps -fu "${TM_USER}" | grep "python NewTaskManager/Worker/worker.py" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_Worker_PID} ]]; then
        _LOG "Worker is running[${_Worker_PID}]."
        echo -n ${_Worker_PID}>"${Worker_PID}"
        return 0
    else
        _ERR "Worker not running."
        return 1
    fi
}

worker_start(){
    worker_status &>/dev/null
    if [[ $? == 0 ]]; then
        _ERR "Worker already running[${_Worker_PID}]"
        exit 1
    else
        nohup python "${Worker_APP}" &>"${BASE_DIR}/run/worker.out" &
        _Worker_PID=$!
        echo -n ${_Worker_PID} >"${Worker_PID}"
        _LOG "Worker started[PID:${_Worker_PID}]"
    fi
}

worker_stop(){
    worker_status &>/dev/null
    if [[ $? == 0 ]]; then
        kill ${_Worker_PID} &>/dev/null && kill -9 ${_Worker_PID} &>/dev/null
        _LOG "Worker stopped[PID:${_Worker_PID}]."
        rm -f "${Worker_PID}"
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
