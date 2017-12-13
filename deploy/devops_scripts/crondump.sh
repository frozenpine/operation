#!/bin/bash
DUMPTOOL_DIR=$HOME/tools/dumptool

cd $DUMPTOOL_DIR
if [ -e "$DUMPTOOL_DIR/nohup.out" ];then
    rm -rf $DUMPTOOL_DIR/nohup.out
fi

if [ -e "$DUMPTOOL_DIR/resume.con" ];then
    rm -rf $DUMPTOOL_DIR/resume.con
fi

nohup ./dumptool &
sleep 5
echo "======================================"
cat $DUMPTOOL_DIR/nohup.out
echo "======================================"
ret=`grep "Login Failed" $DUMPTOOL_DIR/nohup.out`
if [ -z "${ret}" ];then
    echo "======>dumptool ok"
    exit 0
fi
echo "======>dumptool failed"
ps -ef | grep dumptool | grep -v grep | awk '{print $2}' | xargs kill -9
exit 1

