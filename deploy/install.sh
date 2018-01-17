#! /bin/bash

pushd `dirname $0`
BASE_DIR=`pwd`
popd
INSTALL_LOG="${BASE_DIR}/install.log"
pushd "${BASE_DIR}/../"
APP_DIR=`pwd`
popd

DEPLOY_DIR="${HOME}/qops"

PY_VER_RECOMM="2.7.13"
PY_INSTALL_FILE="${BASE_DIR}/Python-${PY_VER_RECOMM}.tgz"
PY_VIRTUALENV_NAME=".virtual"

RELEASE=

_help() {
    MESSAGE="Usage : install.sh [-h] {python|deploy}"
    printf -v HEAD "%*s" $((${#MESSAGE}+4))
    printf "%s\n# %${#MESSAGE}s #\n" ${HEAD// /#}
    printf "# %s #\n" "${MESSAGE}"
    printf "# %${#MESSAGE}s #\n%s\n" "" ${HEAD// /#}
    printf "Option Descriptions :\n"
    cat <<EOF | column -t -c 2 | sed 's/#/ /g'
-h          Print#this#help#message
PYTHON      Install#python-2.7.13#environment,#must#be#run#under#privileged#user
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
    else
        echo `uname -a` | grep -i cygwin && RELEASE="CYG_WIN"
    fi
}

_installPackages() {
    _checkPlatform
    _pause 3 "Going to install platform specfied packages."
    case ${RELEASE} in
        el6|el7)
            _rpmInstall
        ;;
        Ubuntu)
            _debInstall
        ;;
        CYG_WIN)
            _warning <<EOF
This script run under cyg_win.
Please make sure all packages(Python, pip, virtualenv, etc...) required is installed.
EOF
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

_installPip() {
    pushd "${BASE_DIR}/requirements/pip-9.0.1" &>/dev/null
    python setup.py install
    popd >/dev/null
}

_installVirtualenv() {
    pushd "${BASE_DIR}/requirements/virtualenv-15.1.0" &>/dev/null
    python setup.py install
    popd &>/dev/null
}

_updateSetuptools() {
    pushd "${BASE_DIR}/requirements/setuptools-38.4.0" &>/dev/null
    python setup.py install
    popd &>/dev/null
}

_makeVirtualEnv() {
    pushd "${DEPLOY_DIR}" &>/dev/null
    if [[ ${RELEASE} == "CYG_WIN" ]]; then
        python -m virtualenv ${PY_VIRTUALENV_NAME} --system-site-packages
    else
        python -m virtualenv ${PY_VIRTUALENV_NAME}
    fi
    source ${PY_VIRTUALENV_NAME}/bin/activate
    python -m pip install --no-index --find-links="${BASE_DIR}/requirements" -r "${BASE_DIR}/requirements.txt" --no-cache-dir
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
    _pause 3 "Start to build python"
    pushd "/tmp" &>/dev/null
    tar -xzvf "${PY_INSTALL_FILE}"
    cd Python-*
    make clean
    ./configure --prefix=/usr/local/python-2.7.13 | tee -a "${INSTALL_LOG}"
    make -j4 | tee -a "${INSTALL_LOG}"
    make install | tee -a "${INSTALL_LOG}"
    popd &>/dev/null
    _pause 3 "Python build finished."

    pushd /usr/bin >/dev/null
    rm -f python python2 python-config python2-config &>/dev/null
    ln -s /usr/local/python-2.7.13/bin/python2.7 /usr/bin/python2.7.13
    ln -s python2.7.13 python
    ln -s /usr/local/python-2.7.13/bin/python2.7-config /usr/bin/python2.7.13-config
    ln -s python2.7.13-config python-config
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

    [[ ${RELEASE} == "el7" ]] && {
        _warning <<EOF
This platform in Redhat el7, yum command not compatible with python 2.7.13
Trying to fix this problem by specify yum command with python2.7.5 forcelly.
EOF
        sed -i 's/python.*$/python2\.7/' /usr/bin/yum
        sed -i 's/python.*$/python2\.7/' /usr/libexec/urlgrabber-ext-down
        _warning <<EOF
Problem fixed.
EOF
    }
    popd &>/dev/null
}

_deploy() {
    read -p "Please input deploy dir[default: qops]: " ANS
    [[ -n ${ANS} ]] && DEPLOY_DIR="${DEPLOY_DIR}/${ANS}"
    [[ ! -d "${DEPLOY_DIR}" ]] && {
        _warning "${DEPLOY_DIR} not exists, creating..."
        mkdir -p "${DEPLOY_DIR}"
    }
    read -p "Please input python virtualenv name[default: ${PY_VIRTUALENV_NAME}]: " ANS
    [[ -n ${ANS} ]] && {
        PY_VIRTUALENV_NAME=${ANS}
        sed -i 's/VIRTUALENV=.*$/VIRTUAL='"${PY_VIRTUALENV_NAME}"'/' "${BASE_DIR}/../settings.conf"
    }
    # PY_VIRTUALENV_BASE="${DEPLOY_DIR}/${PY_VIRTUALENV_NAME}"
    _info "Start to copy application files to deploy dir."
    for file_dir in `ls "${APP_DIR}" -I deploy`; do
        _info "Copying ${file_dir} to ${DEPLOY_DIR}"
        cp -rf "${APP_DIR}/${file_dir}" "${DEPLOY_DIR}/"
    done
    _info "Verifying directories..."
    [[ -d "${DEPLOY_DIR}/Logs" ]] && {
        _info "Logs dir exist, cleanning..."
        rm -rf "${DEPLOY_DIR}/Logs/*"
        rm -rf "${DEPLOY_DIR}/Logs/.gitkeep"
    } || {
        _warning "Logs dir not exist, creating..."
        mkdir -p "${DEPLOY_DIR}/Logs"
    }
    [[ -d "${DEPLOY_DIR}/dump" ]] && {
        _info "dump dir exist, cleaning..."
        rm -rf "${DEPLOY_DIR}/dump/*"
        rm -rf "${DEPLOY_DIR}/dump/.gitkeep"
    } || {
        _warning "dump dir not exist, creating..."
        mkdir -p "${DEPLOY_DIR}/dump"
    }
    [[ -d "${DEPLOY_DIR}/run" ]] && {
        _info "run dir exist, cleaning..."
        rm -rf "${DEPLOY_DIR}/run/*"
        rm -rf "${DEPLOY_DIR}/run/.gitkeep"
    } || {
        _warning "run dir not exist, creating..."
        mkdir -p "${DEPLOY_DIR}/run"
    }
    [[ -d "${DEPLOY_DIR}/uploads" ]] && {
        _info "run dir exist, cleaning..."
        rm -rf "${DEPLOY_DIR}/run/.gitkeep"
    } || {
        _warning "uploads dir not exist, creating..."
        mkdir -p "${DEPLOY_DIR}/uploads/csv"
        mkdir -p "${DEPLOY_DIR}/uploads/yaml"
    }

    _makeVirtualEnv

    _pause 5 "Application deployed in \"${DEPLOY_DIR}\""
}


while getopts :hf FLAG; do
    case $FLAG in
        h)
            _help
            exit
        ;;
        f)
            _confirm "Do you want to install python 2.7.13 forcelly?" && {
                PY_FORCE_INSTALL=1
                _checkPlatform && _installPython && exit
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
            [[ ${EUID} -ne 0 && `whoami` != "Administrator" ]] && {
                _error "Python installation must run in privilege mode."
                exit 1
            }
            _installPackages && _pause || exit 1
            _checkPythonVersion && _pause || {
                if [[ $RELEASE != "CYG_WIN" ]]; then
                    _confirm "Did you want to install Python automaticlly?" && \
                        _installPython || exit 1
                else
                    _error "Python version check fail."
                    exit 1
                fi
            }
            _updateSetuptools && _installPip && _installVirtualenv
            chmod a+w "${INSTALL_LOG}"
            _pause 5 "Python installation finished."
        ;;
        "deploy")
            _checkPlatform
            [[ ${EUID} -eq 0 || `whoami` == "Administrator" ]] && {
                _confirm "Did you want to deploy under user root?" && {
                    _deploy
                } || {
                    [[ ${RELEASE} == "CYG_WIN" ]] && {
                        _error<<EOF
Script run under cyg_win, and user auto creation will be failed.
If you want to deploy application without privileged user, 
please create normal user and switch to it manually.
Then run this script width deploy command again.
EOF
                        exit 1
                    }
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
                    su - ${USER} -c "${BASE_DIR}/`basename $0` $*;exit"
                    exit
                }
            } || _deploy
        ;;
        "clean")
            rm -rf "${BASE_DIR}/../"
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
