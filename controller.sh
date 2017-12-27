#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/controller.log"
cd  ${BASE_DIR}

CONTROLLER_APP="${BASE_DIR}/NewTaskManager/Controller/testing/server.py"
CONTROLLER_PID="${BASE_DIR}/run/controller.pid"
TM_USER="${UID}"
_CONTROLLER_PID=

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

controller_status(){
    if [[ -f "${CONTROLLER_PID}" ]]; then
        _CONTROLLER_PID=`cat "${CONTROLLER_PID}"`
        kill -0 ${_CONTROLLER_PID} &>/dev/null
        if [[ $? == 0 ]]; then
            _LOG "Controller is running[${_CONTROLLER_PID}]."
            return 0
        else
            _CONTROLLER_PID=
            _ERR "Controller pid file is incorrect, cleaned."
            rm -f "${CONTROLLER_PID}"
        fi
    fi
    _CONTROLLER_PID=`ps -fu "${TM_USER}" | grep "/Controller/testing/server.py" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_CONTROLLER_PID} ]]; then
        _LOG "Controller is running[${_CONTROLLER_PID}]."
        echo -n ${_CONTROLLER_PID}>"${CONTROLLER_PID}"
        return 0
    else
        _ERR "Controller not running."
        return 1
    fi
}

controller_start(){
    controller_status &>/dev/null
    if [[ $? == 0 ]]; then
        _ERR "Controller already running[${_CONTROLLER_PID}]"
        exit 1
    else
        nohup python "${CONTROLLER_APP}" &>"${BASE_DIR}/run/controller.out" &
        _CONTROLLER_PID=$!
        echo -n ${_CONTROLLER_PID} >"${CONTROLLER_PID}"
        _LOG "Controller started[PID:${_CONTROLLER_PID}]"
    fi
}

controller_stop(){
    controller_status &>/dev/null
    if [[ $? == 0 ]]; then
        kill ${_CONTROLLER_PID} &>/dev/null && kill -9 ${_CONTROLLER_PID} &>/dev/null
        _LOG "Controller stopped[PID:${_CONTROLLER_PID}]."
        rm -f "${CONTROLLER_PID}"
    else
        _ERR "Controller already stopped."
        exit 1
    fi
}

case $1 in
    'start')
        controller_start
    ;;
    'stop')
        controller_stop
    ;;
    'status')
        controller_status
    ;;
    'restart')
        controller_stop
        sleep 3
        controller_start
    ;;
    *)
        echo "Usage: `basename $0` [start|stop|status|restart]" >&2
        exit 1
    ;;
esac
