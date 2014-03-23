#!/bin/bash

export WILL_ROOMS='Hipnos is only the beginning'

`find . -name "start_dev_will.py"` &
PID=$!
sleep 10
RUNNING=`ps a | grep start_dev_will | grep -v grep | wc -l`
if [ ${RUNNING} -gt 0 ]; then
    kill $PID
    ps a | grep start_dev_will | grep -v grep | awk '{print $1}' | xargs kill -9
    exit 0;
else
    exit 1;
fi
