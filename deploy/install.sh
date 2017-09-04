#! /bin/bash

pushd `dirname $0`
BASE_DIR=`pwd`
popd
INSTALL_LOG="${BASE_DIR}/install.log"
pushd "${BASE_DIR}/../"
APP_DIR=`pwd`
popd

DEPLOY_DIR="${HOME}"

PY_VER_RECOMM="2.7.13"
PY_INSTALL_FILE="${BASE_DIR}/Python-${PY_VER_RECOMM}.tgz"
PY_VIRTUALENV_NAME="devops"
PY_VIRTUALENV_BASE=

RELEASE=

_help() {
    MESSAGE="Usage : install.sh [-h] {python|deploy}"
    printf -v HEAD "%*s" $((${#MESSAGE}+4))
    printf "%s\n# %${#MESSAGE}s #\n" ${HEAD// /#}
    printf "# %s #\n" "${MESSAGE}"
    printf "# %${#MESSAGE}s #\n%s\n" "" ${HEAD// /#}
    printf "Option Descriptions :\n"
    cat <<EOF | column -t -c 2 | sed 's/#/ /g'
PYTHON      Install#python-2.7.*#environment,#must#be#run#under#privileged#user.
DEPLOY      Deploy#application
EOF
}

_pause() {
    [[ $1 =~ [0-9] ]] && {
        local TIMEOUT=$1
        shift 1
    }
    [[ ! ${TIMEOUT} ]] && {
        echo "$*"
        read -n1 -p "Press any key to continue..."
        echo
    } || {
        echo "$*"
        read -n1 -t ${TIMEOUT} -p "Press any key or wait for ${TIMEOUT} seconds to continue..."
        echo
    }
}

_confirm() {
    local MESSAGE
    local ANS
    while true; do
        [[ $# -gt 0 ]] && MESSAGE="$* (y|n)" || MESSAGE="Confirmed? (y|n)"
        read -n1 -p "${MESSAGE}" ANS
        case ${ANS} in
            Y|y)
                echo
                return 0
            ;;
            N|n)
                echo
                return 1
            ;;
            *)
                echo; echo "Invalid input."
                continue
            ;;
        esac
    done
}

_error() {
    [[ $# > 0 ]] && {
        echo "`date` [ERROR] $*" | tee -a "${INSTALL_LOG}" 1>&2
    } || {
        cat | sed -e 's/\(.*\)/    \1/g' -e '1 i\'"`date`"' [ERROR]' | tee -a "${INSTALL_LOG}" 1>&2
    }
}

_warning() {
    [[ $# > 0 ]] && {
        echo "`date` [WARNING] $*" | tee -a "${INSTALL_LOG}" 1>&2
    } || {
        cat | sed -e 's/\(.*\)/    \1/g' -e '1 i\'"`date`"' [WARNING]' | tee -a "${INSTALL_LOG}" 1>&2
    }
}

_info() {
    [[ $# -gt 0 ]] && {
        echo "`date` [INFO] $*" | tee -a "${INSTALL_LOG}"
    } || {
        cat | sed -e 's/\(.*\)/    \1/g' -e '1 i\'"`date`"' [INFO]' | tee -a "${INSTALL_LOG}"
    }
}

_checkPlatform() {
    _info "Checking system platform..."
    if [[ -f /etc/redhat-release ]]; then
        RELEASE=`uname -r|awk -F'.' '{print $(NF-1)}'`
        _info "Current system platform is redhat ${RELEASE}."
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
    [[ ${PY_VER_MAJ} -gt 2 ]] && {
        _error <<EOF
Python major version(${PY_VER_MAJ}) check faild.
Version 2.7.* is required, version ${PY_VER_RECOMM} is recommanded.
EOF
        return 1
    } || {
        [[ ${PY_VER_MIN} -lt 7 ]] && {
            _error <<EOF
Python minor version(${PY_VER_MIN}) check faild.
Version 2.7.* is required, version ${PY_VER_RECOMM} is recommanded.
EOF
            return 1
        } || {
            [[ ${PY_VER_REL} -ne 13 ]] && {
                _warning <<EOF
Python version(${PY_VER}) meet requirement, but not fully tested.
Version 2.7.* is required, version ${PY_VER_RECOMM} is recommanded.
EOF
            } || _info "Python version fully meet requirement."
        }
    }
}

_checkPip() {
    which pip &>/dev/null
    [[ $? -ne 0 ]] && {
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
    } || _info "Pip module check successfully"
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
    [[ -d "${BASE_DIR}/packages" ]] && {
        pushd "${BASE_DIR}/packages" &>/dev/null
        pushd "/etc/yum.repos.d" &>/dev/null
        mkdir qt_repoback; mv *.repo qt_repoback/
        yum clean all &>/dev/null
        popd &>/dev/null
        cd ${RELEASE} && {
            yum localinstall -y *.rpm
            pushd "/etc/yum.repos.d" &>/dev/null
            mv qt_repoback/*.repo ./; rm -rf qt_repoback
            popd &>/dev/null
        } || {
            _error "No packages dir for ${RELEASE}."
            exit 1
        }
        _info "Pre-install packages finished."
        popd &>/dev/null
    } || {
        _error "RPM packages directory missing."
        exit 1
    }
}

_debInstall() {
    _error "DEB packetge installation not implemented."
}

_installPython() {
    pushd "/tmp" &>/dev/null
    tar -xzvf "${PY_INSTALL_FILE}"
    cd Python-*
    ./configure
    make -j4; make install -k
    rm -f /usr/bin/python
    ln -s /usr/bin/python /usr/local/bin/python2.7
    popd &>/dev/null
    [[ ${RELEASE} == "el6" ]] && {
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
    }
}

_deploy() {
    read -p "Please input deploy base dir[default: ${DEPLOY_DIR}]: " ANS
    [[ -n ${ANS} ]] && DEPLOY_DIR=${ANS}
    [[ ! -d "${DEPLOY_DIR}" ]] && {
        _warning "${DEPLOY_DIR} not exists, creating..."
        mkdir -p "${DEPLOY_DIR}"
    }
    read -p "Please input python virtualenv name[default: ${PY_VIRTUALENV_NAME}]: " ANS
    [[ -n ${ANS} ]] && PY_VIRTUALENV_NAME=${ANS}
    PY_VIRTUALENV_BASE="${DEPLOY_DIR}/${PY_VIRTUALENV_NAME}"
    _makeVirtualEnv
    _info "Start to copy application files to virtual environment."
    for file_dir in `ls "${APP_DIR}" -I deploy`; do
        _info "Copying ${file_dir} to ${PY_VIRTUALENV_BASE}"
        cp -rf "${APP_DIR}/${file_dir}" "${PY_VIRTUALENV_BASE}/"
    done
    _info "Granting privileges to starter scripts."
    chmod a+x "${PY_VIRTUALENV_BASE}/*.sh"
    _info "Verifying directories..."
    [[ -d "${PY_VIRTUALENV_BASE}/Logs" ]] && {
        _info "Logs dir exist, cleanning..."
        rm -rf "${PY_VIRTUALENV_BASE}/Logs/*"
    } || {
        _warning "Logs dir not exist, creating..."
        mkdir -p "${PY_VIRTUALENV_BASE}/Logs"
    }
    [[ -d "${PY_VIRTUALENV_BASE}/dump" ]] && {
        _info "dump dir exist, cleaning..."
        rm -rf "${PY_VIRTUALENV_BASE}/dump/*"
    } || {
        _warning "dump dir not exist, creating..."
        mkdir -p "${PY_VIRTUALENV_BASE}/dump"
    }
    [[ -d "${PY_VIRTUALENV_BASE}/run" ]] || {
        _warning "run dir not exist, creating..."
        mkdir -p "${PY_VIRTUALENV_BASE}/run"
    }
    [[ -d "${PY_VIRTUALENV_BASE}/uploads" ]] || {
        _warning "uploads dir not exist, creating..."
        mkdir -p "${PY_VIRTUALENV_BASE}/uploads/csv"
        mkdir -p "${PY_VIRTUALENV_BASE}/uploads/yaml"
    }
    _pause 5 "Application deployed in \"$PY_VIRTUALENV_BASE}\""
}


while getopts :hf FLAG; do
    case $FLAG in
        h)
            _help
            exit
        ;;
        f)
            _confirm "Do you want to install python 2.7.13 forcelly?" && {
                _installPython
            } || exit 1
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
            local ANS
            [[ ${EUID} -ne 0 ]] && {
                _error "Python installation must run in privilege mode."
                exit 1
            }
            _checkPlatform && _pause || exit 1
            _checkPythonVersion && _pause || {
                _confirm "Did you want to install Python automaticlly?" && \
                    _installPython || exit 1
            }
            _checkPip && {
                _pause
                _installVirtualenv
            }
            _pause 5 "Python installation finished."
        ;;
        "deploy")
            [[ ${EUID} -eq 0 ]] && {
                _confirm "Did you want to deploy under user root?" && {
                    _deploy
                } || {
                    while true; do
                        read -p "Please input username: " USER
                        grep ${USER} /etc/passwd && {
                            _confirm "User exist, did you mean deploy under exist user \"${USER}\"" && \
                                break || continue
                        } || {
                            useradd ${USER}
                            while true; do
                                read -p "Please input password: " PASSWORD
                                [[ -n ${PASSWORD} ]] && {
                                    echo -n "${PASSWORD}" | passwd ${USER} --stdin
                                    break
                                } || {
                                    _warning "Password can not be empty."
                                    continue
                                }
                            done
                            break
                        }
                    done
                    su - ${USER} -c "${BASE_DIR}/`basename $0` $*"
                }
            } || _deploy
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
