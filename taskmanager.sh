#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/taskmanager.log"
cd  ${BASE_DIR}

TM_APP="${BASE_DIR}/TaskManager/main.py"
TM_PID="${BASE_DIR}/run/taskmanager.pid"
TM_USER="devops"
_PID=

# switch to python virtual env
source "${BASE_DIR}/bin/activate"

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

tm_status(){
    if [[ -f "${TM_PID}" ]]; then
        _PID=`cat "${TM_PID}"`
        kill -0 ${_PID} &>/dev/null
        if [[ $? == 0 ]]; then
            _LOG "TaskManager is running[${_PID}]."
            return 0
        else
            _PID=
            _ERR "TaskManager pid file is incorrect, cleaned."
            rm -f "${TM_PID}"
        fi
    fi
    _PID=`ps -fu "${TM_USER}" | grep "python TaskManager/main.py" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_PID} ]]; then
        _LOG "TaskManager is running[${_PID}]."
        echo -n ${_PID}>"${TM_PID}"
        return 0
    else
        _ERR "TaskManager not running."
        return 1
    fi
}

tm_start(){
    tm_status &>/dev/null
    if [[ $? == 0 ]]; then
        _ERR "TaskManager already running[${_PID}]"
        exit 1
    else
        nohup python "${TM_APP}" &>"${BASE_DIR}/run/taskmanager.out" &
        _PID=$!
        echo -n ${_PID} >"${TM_PID}"
        _LOG "TaskManager started[PID:${_PID}]"
    fi
}

tm_stop(){
    tm_status &>/dev/null
    if [[ $? == 0 ]]; then
        kill ${_PID} &>/dev/null && kill -9 ${_PID} &>/dev/null
        _LOG "TaskManager stopped[PID:${_PID}]."
        rm -f "${TM_PID}"
    else
        _ERR "TaskManager already stopped."
        exit 1
    fi
}

case $1 in
    'start')
        tm_start
    ;;
    'stop')
        tm_stop
    ;;
    'status')
        tm_status
    ;;
    'restart')
        tm_stop
        tm_start
    ;;
    *)
        echo "Usage: `basename $0` [start|stop|status|restart]" >&2
        exit 1
    ;;
esac
