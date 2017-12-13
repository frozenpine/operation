#!/bin/bash
ListDB=$HOME/list/list.db
WebHost=`cat $ListDB | awk '{print $2}'`

ret=`curl http://${WebHost}:8080/quantdo/restfulservice/busAuditService/anonymousAuditAfterToTrade` 1>/dev/null 2>/dev/null

if [ -z $ret ];then
    echo "[ERR] ���ݻ���ʧ�ܣ������̨����"
    exit 1
else
    sFalse=`echo $ret | grep false` 
    if [ -z $sFalse ];then
        echo "[OK] ���ݻ��˳ɹ�"
    else
        echo "============================================================="
        echo "���˽����"$ret
        echo "============================================================="
        echo "[ERR] ���ݻ���ʧ�ܣ������̨����"
        exit 1
    fi
fi
exit 0

