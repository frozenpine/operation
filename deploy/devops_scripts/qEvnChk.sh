#!/bin/bash
ListRun=$HOME/list/list.run
ShowDetail=0

Chk_proc()
{
    bCheckOK=1;
    while read line
    do
        param=`echo $line | awk '{print $4}'`
        num=`echo $line | awk '{print $5}'`
        user=`echo $line | awk '{print $2}'`
        #pid=`ps -fu $user | grep $param$num | grep -v grep | awk '{print $2}'`
        if [ $1 == "start" ];then
            if [ -z $num ]; then
                pid=`ps -fu $user | grep $param | grep -v grep | awk '{print $2}'`
                if [ -z $pid ];then
                    echo "[ERR] $param not exist, check error!!!"
                    bCheckOK=0;
                else
                    if [ $ShowDetail == 1 ];then
                        echo "[$param] =======> pid = [$pid]" 
                    fi
                fi
            else
                pid=`ps -fu $user | grep "$param $num" | grep -v grep | awk '{print $2}'`
                if [ -z $pid ];then
                    echo "[ERR] $param$num not exist, check error!!!"
                    bCheckOK=0;
                else
                    if [ $ShowDetail == 1 ];then
                        echo "[$param$num] =======> pid = [$pid]" 
                    fi
                fi
            fi   
        fi
        if [ $1 == "stop" ];then
            if [ -z $num ]; then
                pid=`ps -fu $user | grep $param | grep -v grep | awk '{print $2}'`
                if [ -z $pid ];then
                    if [ $ShowDetail == 1 ];then
                        echo "$param =======> stop" 
                    fi
                else
                    echo "[ERR] $param exist, check error!!!"
                    bCheckOK=0;
                fi
            else
                pid=`ps -fu $user | grep "$param $num" | grep -v grep | awk '{print $2}'`
                if [ -z $pid ];then
                    if [ $ShowDetail == 1 ];then
                        echo "$param$num =======> stop" 
                    fi
                else
                    echo "[ERR] $param$num exist, check error!!!"
                    bCheckOK=0;
                fi
            fi
        fi
    done < $ListRun
    if [ $bCheckOK == 1 ];then
        echo "[OK] All process is "$1"ed, check ok."
    else
        exit 1
    fi
}

Chk_flow()
{
    ret=`find ~/qtrade/flow -name "TradeResult.con"`
    if [ -z "$ret" ];then
	echo "[OK] Clean flow success"
        exit 0
    else
	echo "[ERR] Clean flow failed"
        if [ $ShowDetail == 1 ];then
            echo "=============detail flow============="
            exit 1
        fi
    fi
}

Chk_oper_database()
{
    $HOME/bin/chkall.sh
    exit $?
}

EchoUsage()
{
	echo "Usage: $0 @cmdNum [@showdetail]"
		echo "  [cmdNum]:"
		echo "    1 - check process status start"
		echo "    2 - check process status stop"
		echo "    3 - check clean flow"
		echo "    4 - check clean oper database"
		echo "  [showdetail]:"
		echo "    0 - not show detail log"
		echo "    1 - show detail log"
}

main()
{
	if [ $# == 0 ]; then
        EchoUsage;
        exit 1
	fi
    #$2=1,show detail log
    if [ $# == 2 ];then
	    if [ $2 == 1 ] ;then
	       ShowDetail=1 
	    fi
    fi
    #check process start
	if [ $1 == 1 ] ;then
	    Chk_proc "start";
	fi
    #check process stop
	if [ $1 == 2 ] ;then
	    Chk_proc "stop";
	fi
    #check clean flow 
	if [ $1 == 3 ] ;then
	    Chk_flow;
	fi
    #check clean oper database
	if [ $1 == 4 ] ;then
	    Chk_oper_database;
	fi

       exit 0
}

main $@;
