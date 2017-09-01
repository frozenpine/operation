#! /bin/bash

cd `dirname $0`
BASE_DIR=`pwd`
INSTALL_LOG="${BASE_DIR}/install.log"

DEPLOY_DIR="${HOME}"

PY_VER_RECOMM="2.7.13"
PY_INSTALL_FILE="${BASE_DIR}/Python-${PY_VER_RECOMM}.tgz"
PY_VIRTUALENV_NAME="devops"

RELEASE=

_help() {
    MESSAGE="Usage : install.sh [-h] {python|deploy}"
    printf -v HEAD "%*s" $((${#MESSAGE}+4))
    printf "%s\n# %${#MESSAGE}s #\n" ${HEAD// /#}
    printf "# %s #\n" "${MESSAGE}"
    printf "# %${#MESSAGE}s #\n%s\n" "" ${HEAD// /#}
    printf "Option Descriptions :\n"
    cat <<EOF | column -t -c 2 | sed 's/#/ /g'
PYTHON      Install#python-2.7.*#environment
DEPLOY      Deploy#application
EOF
}

_pause() {
    if [[ $1 =~ [0-9] ]]; then
        local TIMEOUT=$1
        shift 1
    fi
    if [[ ! ${TIMEOUT} ]]; then
        echo "$*"
        read -n1 -p "Press any key to continue..."
        echo
    else
        echo "$*"
        read -n1 -t ${TIMEOUT} -p "Press any key or wait for ${TIMEOUT} seconds to continue..."
        echo
    fi
}

_error() {
    if [[ $# > 0 ]]; then
        echo "`date` [ERROR] $*" | tee -a "${INSTALL_LOG}" 1>&2
    else
        cat | sed -e 's/\(.*\)/    \1/g' -e '1 i\'"`date`"' [ERROR]' | tee -a "${INSTALL_LOG}" 1>&2
    fi
}

_warning() {
    if [[ $# > 0 ]]; then
        echo "`date` [WARNING] $*" | tee -a "${INSTALL_LOG}" 1>&2
    else
        cat | sed -e 's/\(.*\)/    \1/g' -e '1 i\'"`date`"' [WARNING]' | tee -a "${INSTALL_LOG}" 1>&2
    fi
}

_info() {
    if [[ $# > 0 ]]; then
        echo "`date` [INFO] $*" | tee -a "${INSTALL_LOG}"
    else
        cat | sed -e 's/\(.*\)/    \1/g' -e '1 i\'"`date`"' [INFO]' | tee -a "${INSTALL_LOG}"
    fi
}

_checkPlatform() {
    _info "Checking system platform..."
    if [[ -f /etc/redhat-release ]]; then
        RELEASE=`uname -r|awk -F'.' '{print $(NF-1)}'`

        _info "Current system platform is redhat ${RELEASE}."
        if [[ ${RELEASE} == "el6" ]]; then
            _warning <<EOF
This platform in Redhat el6, yum command not compatible with python 2.7.*
Trying to fix this problem by specify yum command with python2.6 forcelly.
Current config: `head -1 /usr/bin/yum`
EOF
            sed -i 's/python.*$/python2\.6/' /usr/bin/yum
            _warning <<EOF
Problem fixed.
New config: `head -1 /usr/bin/yum`
EOF
        fi
    elif [[ -f /etc/lsb-release ]]; then
        RELEASE=`grep DISTRIB_ID /etc/lsb-release|cut -d'=' -f2`
        _info "Current system platform is ${RELEASE}."
    fi
    _pause 3 "Going to install platform specfied packages."
    case ${RELEASE} in
        el6|el7)
            _rpmInstall
        ;;
        Ubuntu)
            _debInstall
        ;;
        *)
            _error "This linux release not supported by `basename $0`, please deploy manually."
            return 1
        ;;
    esac
}

_checkPythonVersion() {
    which python &>/dev/null || return 1
    PY_VER=$(python -V 2>&1|cut -d' ' -f2)
    #PY_VER="3.7.5"
    PY_VER_MAJ=$(echo ${PY_VER}|cut -d'.' -f1)
    PY_VER_MIN=$(echo ${PY_VER}|cut -d'.' -f2)
    PY_VER_REL=$(echo ${PY_VER}|cut -d'.' -f3|sed 's/[^0-9]$//g')
    _info "Current python version: ${PY_VER}"
    if [[ ${PY_VER_MAJ} -gt 2 ]]; then
        _error <<EOF
Python major version(${PY_VER_MAJ}) check faild.
Version 2.7.* is required, version ${PY_VER_RECOMM} is recommanded.
EOF
        return 1
    else
        if [[ ${PY_VER_MIN} -lt 7 ]]; then
            _error <<EOF
Python minor version(${PY_VER_MIN}) check faild.
Version 2.7.* is required, version ${PY_VER_RECOMM} is recommanded.
EOF
            return 1
        else
            if [[ ${PY_VER_REL} -ne 13 ]]; then
                _warning <<EOF
Python version(${PY_VER}) meet requirement, but not fully tested.
Version 2.7.* is required, version ${PY_VER_RECOMM} is recommanded.
EOF
            else
                _info "Python version fully meet requirement."
            fi
        fi
    fi
}

_checkPip() {
    which pip &>/dev/null
    if [[ $? -ne 0 ]]; then
        pushd "/tmp" &>/dev/null
        pushd "${BASE_DIR}/requirements" &>/dev/null
        SETUPTOOL_FILE=`ls setuptools-*.zip`
        popd &>/dev/null
        unzip "${BASE_DIR}/requirements/${SETUPTOOL_FILE}"
        cd setuptools-*
        python setup.py install
        pushd "${BASE_DIR}/requirements" &>/dev/null
        PIP_FILE=`ls pip-*.tar.gz`
        popd &>/dev/null
        tar -xzvf "${BASE_DIR}/requirements/${PIP_FILE}"
        cd pip-*
        python setup.py install
        popd &>/dev/null
        _info "Pip installed successfully."
    else
        _info "Pip module check successfully"
    fi
}

_installVirtualenv() {
    _checkPip
    which virtualenv &>/dev/null && {
        _info "Virtualenv already installed."
    } || {
        pushd "${BASE_DIR}/requirements/" &>/dev/null
        pip install virtualenv*.tar.gz
        popd &>/dev/null
    }
}

_makeVirtualEnv() {
    pushd "${DEPLOY_DIR}" &>/dev/null
    virtualenv ${PY_VIRTUALENV_NAME}
    source ${PY_VIRTUALENV_NAME}/bin/activate
    if [[ ${RELEASE} == "el6" ]]; then
        pip install --find-links="${BASE_DIR}/requirements" -r "${BASE_DIR}/requirements.txt"
    else
        pip install --no-index --find-links="${BASE_DIR}/requirements" -r "${BASE_DIR}/requirements.txt"
    fi
    deactivate
    popd &>/dev/null
}

_rpmInstall() {
    if [[ -d "${BASE_DIR}/packages" ]]; then
        pushd "${BASE_DIR}/packages" &>/dev/null
        pushd "/etc/yum.repos.d" &>/dev/null
        mkdir qt_repoback; mv *.repo qt_repoback/
        yum clean all &>/dev/null
        popd &>/dev/null
        cd ${RELEASE}
        yum localinstall -y *.rpm
        pushd "/etc/yum.repos.d" &>/dev/null
        mv qt_repoback/*.repo ./; rm -rf qt_repoback
        popd &>/dev/null
        _info "Pre-install packages finished."
        popd &>/dev/null
    else
        _error "RPM packages directory missing."
    fi
}

_debInstall() {
    _error "DEB packetge installation not implemented."
}

_installPython() {
    pushd "/tmp" &>/dev/null
    tar -xzvf "${PY_INSTALL_FILE}"
    cd Python-*
    ./configure
    make -j4; make install
    rm -f /usr/bin/python
    ln -s /usr/bin/python /usr/local/bin/python2.7
    popd &>/dev/null
}


while getopts :h FLAG; do
    case $FLAG in
        h)
            _help
            exit
        ;;
        *)
            _help >&2
            exit 1
        ;;
    esac
done
shift $((OPTIND-1))
[ $# -eq 1 ] && {
    case $1 in
        "python")
            [[ ${EUID} -ne 0 ]] && {
                _error "Python installation must run in privilege mode."
                exit 1
            }
            _checkPlatform && _pause || exit 1
            _checkPythonVersion && _pause || {
                while true; do
                    read -t 10 -n1 -p "Did you want to install Python automaticlly?(Y or n)" ANS || {
                        _error "Read timeout(10s), automatically answner yes."
                        ${ANS}=y
                    }
                    case ${ANS} in
                        Y|y)
                            echo
                            break
                        ;;
                        N|n)
                            echo
                            exit 1
                        ;;
                        *)
                            _error "Invalid input, retry."
                            continue
                        ;;
                    esac
                done
                _installPython
            }
            _checkPip && {
                _pause
                _installVirtualenv
            }
            _pause 5 "Python installation finished."
        ;;
        "deploy")
            _makeVirtualEnv
            _pause 5 "Application deployed in \"${DEPLOY_DIR}/${PY_VIRTUALENV_NAME}\""
        ;;
        *)
            echo "$(basename $0) illegal option -- $1" >&2
            _help >&2
            exit 1
        ;;
    esac
} || {
    echo "$(basename $0) illegal option -- $*" >&2
    _help >&2
    exit 1
}
