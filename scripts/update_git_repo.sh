#!/usr/bin/env bash
set -eu

SRC_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}); cd ../; pwd)

cd $SRC_DIR
git fetch origin master
git merge origin/master --no-edit
git push origin HEAD:master
