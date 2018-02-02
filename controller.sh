#! /bin/bash

BASE_DIR=`dirname $0`
LOG_FILE="${BASE_DIR}/run/controller.log"
cd ${BASE_DIR}

CONTROLLER_APP="TaskManager/Controller/server.py"
CONTROLLER_PID="run/controller.pid"
TM_USER="${UID}"
_CONTROLLER_PID=

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

controller_status(){
    if [[ -f "${CONTROLLER_PID}" ]]; then
        _CONTROLLER_PID=`cat "${CONTROLLER_PID}"`
        kill -0 ${_CONTROLLER_PID} &>/dev/null
        if [[ $? == 0 ]]; then
            ps -fu ${TM_USER} | awk '$2=='${_CONTROLLER_PID}' && $0 ~/'"`basename ${CONTROLLER_APP}`"'/{print}' | grep python &>/dev/null
            if [[ $? == 0 ]]; then
                _LOG "Controller[${_CONTROLLER_PID}] is running."
                echo
                return 0
            fi
        fi
        _CONTROLLER_PID=
        _ERR "Incorrect pid file, clean pid file."
        echo
        rm -f "${CONTROLLER_PID}"
    fi
    _CONTROLLER_PID=`ps -fu "${TM_USER}" | grep "${CONTROLLER_APP}" | awk '$0 !~/grep|awk|vim?|nano/{print $2}'`
    if [[ -n ${_CONTROLLER_PID} ]]; then
        _LOG "Controller[${_CONTROLLER_PID}] is running."
        echo
        echo -n ${_CONTROLLER_PID}>"${CONTROLLER_PID}"
        return 0
    else
        _LOG "Controller not running."
        echo
        return 1
    fi
}

controller_start(){
    controller_status &>/dev/null
    if [[ $? == 0 ]]; then
        echo
        _ERR "Controller[${_CONTROLLER_PID}] is already running."
        echo
        return 1
    else
        # switch to python virtual env
        source "${BASE_DIR}/${VIRTUALENV}/bin/activate"
        echo
        _LOG "Starting Controller"
        nohup python "${CONTROLLER_APP}" &>"${BASE_DIR}/run/controller.out" &
        _CONTROLLER_PID=$!
        echo -n ${_CONTROLLER_PID} >"${CONTROLLER_PID}"
        controller_status
    fi
}

controller_stop(){
    controller_status &>/dev/null
    if [[ $? == 0 ]]; then
        echo
        _LOG "Stopping Controller."
        kill ${_CONTROLLER_PID} &>/dev/null
        while true; do
            controller_status &>/dev/null
            if [[ $? == 0 ]]; then
                kill -9 ${_CONTROLLER_PID} &>/dev/null
                sleep 1
            else
                break
            fi
        done
        while true; do
            netstat -tan | grep "${RPC_PORT}" >/dev/null
            if [[ $? == 0 ]]; then
                sleep 1
            else
                break
            fi
        done
        controller_status
    else
        echo
        _ERR "Controller already stopped."
        echo
        return 1
    fi
}

case $1 in
    'start')
        controller_start || exit 1
    ;;
    'stop')
        controller_stop || exit 1
    ;;
    'status')
        echo
        controller_status || exit 1
    ;;
    'restart')
        controller_stop
        controller_start || exit 1
    ;;
    *)
        echo "Usage: `basename $0` [start|stop|status|restart]" >&2
        exit 1
    ;;
esac
