#! /bin/bash

LIST_DB="${HOME}/list/list.db"
DB_HOST=
DB_USER=
DB_PWD=
DB_NAME=

while read tag1i db_host db_user db_pwd db_name tag2; do
	DB_HOST=$db_host
	DB_USER=$db_user
	DB_PWD=$db_pwd
	DB_NAME=$db_name
done<"${LIST_DB}"

SETTLE_STATUS=`mysql -N -h${DB_HOST} -u${DB_USER} -p${DB_PWD} ${DB_NAME} -e "SELECT t.settle_status FROM t_settle_status t WHERE t.settle_date=(SELECT tradingday FROM t_sync_systemstatus LIMIT 1) ORDER BY t.settle_status DESC LIMIT 1"`

if [[ ${SETTLE_STATUS} != '3' ]]; then
	echo "Please wait for settlement."
	exit 1
else
	echo "All settled."
fi
