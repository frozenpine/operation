#! /bin/bash

BASE_DIR=`dirname $0`
BACK_DIR="${BASE_DIR}/`whoami`backup"
BACK_FILE="${BACK_DIR}/`whoami`_`date '+%Y%m%d%H%M%S'`.tar.gz"

[[ ! -d "${BACK_DIR}" ]] && mkdir -p "${BACK_DIR}"

tar -czvf "${BACK_FILE}" */bin/*.log */flow/*

ls -lh "${BACK_FILE}"
