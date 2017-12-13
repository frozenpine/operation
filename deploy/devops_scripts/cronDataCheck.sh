#!/bin/bash
ListDB=$HOME/list/list.db
DatabaseHost=`cat $ListDB | awk '{print $2}'`

ret=`curl http://${DatabaseHost}:8080/quantdo/restfulservice/busAuditService/anonymousAuditAfterToTrade` 1>/dev/null 2>/dev/null

if [ -z $ret ];then
    echo "[ERR] 数据稽核失败，请检查后台数据"
    exit 1
else
    sFalse=`echo $ret | grep false` 
    if [ -z $sFalse ];then
        echo "[OK] 数据稽核成功"
    else
        echo "============================================================="
        echo "稽核结果："$ret
        echo "============================================================="
        echo "[ERR] 数据稽核失败，请检查后台数据"
        exit 1
    fi
fi
exit 0

