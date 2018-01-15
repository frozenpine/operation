#! /bin/bash

BASE_DIR=`dirname $0`
cd ${BASE_DIR}

INIT_APP=init.py

[[ -s "${BASE_DIR}/settings.conf" ]] && source "${BASE_DIR}/settings.conf" || {
    echo '"settings.conf" not found!' >&2
    exit 1
}

# switch to python virtual env
[[ -f "${BASE_DIR}/${VIRTUALENV}/bin/activate" ]] && source "${BASE_DIR}/${VIRTUALENV}/bin/activate" || {
    echo "Virtual enviroment not exist." >&2
    exit 1
}

python ${INIT_APP} drop_db || {
    echo "Faild to clean db." >&2
    exit 1
}
python ${INIT_APP} create_db || {
    echo "Faild to create db tables." >&2
    exit 1
}
python ${INIT_APP} init_auth || {
    echo "Faild to init auth info." >&2
    exit 1
}
python ${INIT_APP} init_inventory || {
    echo "Faild to init inventory info." >&2
    exit 1
}
python ${INIT_APP} init_operation || {
    echo "Faild to init operation catalog." >&2
    exit 1
}
