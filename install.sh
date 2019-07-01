#!/usr/bin/env bash
set -eu

SRC_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
mkdir -p $SRC_DIR/tmp
crontab -l 2> /dev/null 1> $SRC_DIR/tmp/crontab 
echo "* * * * * $SRC_DIR/ambient_logger/run.sh > /dev/shm/ambient_logger.log 2>&1" >> $SRC_DIR/tmp/crontab
crontab $SRC_DIR/tmp/crontab
