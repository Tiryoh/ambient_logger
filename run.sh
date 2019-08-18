#!/usr/bin/env bash
set -eu

SRC_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)

AMBIENT_ENV="ROOM"

SLACK_WEBHOOK="https://hooks.slack.com/services/"
SLACK_POST_CH="#ramdom"
SLACK_POST_USERNAME="ambient_sensor"
SLACK_POST_EMOJI=":fastparrot:"

AMBIENTIO_ID="9999999"
AMBIENTIO_WKEY="YourAmbientIoWriteKey"
FIREBASE_KEY="YourFirebaseServiceAccountKey.json"

if [[ -e ${SRC_DIR}/.env.sh ]]; then
	source ${SRC_DIR}/.env.sh
fi

cd ${SRC_DIR}
RESULT=$(./ambient_logger.py --id="${AMBIENTIO_ID}" --wkey="${AMBIENTIO_WKEY}" --firebase="${FIREBASE_KEY}")
echo $RESULT
RESULT=$(echo $RESULT | grep "d1")

CO2=$(echo $RESULT | sed -e "s/.*'d1': \([0-9]*\).*/\1/g")
TEMP=$(echo $RESULT | sed -e "s/.*'d2': \([0-9]*\).*/\1/g")
HUM=$(echo $RESULT | sed -e "s/.*'d3': \([0-9]*\).*/\1/g")

touch /dev/shm/logger_co2_flag
touch /dev/shm/logger_temp_flag
touch /dev/shm/logger_co2
touch /dev/shm/logger_temp
touch /dev/shm/logger_hum
touch /dev/shm/logger_timestamp

CO2_FLAG=$(cat /dev/shm/logger_co2_flag)
TEMP_FLAG=$(cat /dev/shm/logger_temp_flag)
MSG=""

if [[ $CO2 -gt 2000 ]]; then
	MSG+="${AMBIENT_ENV}の二酸化炭素濃度が極めて高いです。$CO2 ppmです。"
elif [[ $CO2 -gt 1500 ]] && [[ $CO2_FLAG -eq 0 ]]; then
	MSG+="${AMBIENT_ENV}の二酸化炭素濃度が高いです。$CO2 ppmです。"
	export CO2_FLAG=1
elif [[ $CO2 -lt 1400 ]] && [[ $CO2_FLAG -eq 1 ]]; then
	MSG+="${AMBIENT_ENV}の二酸化炭素濃度が$CO2 ppmまで下がりました。"
	export CO2_FLAG=0
fi

if [[ $TEMP -gt 32 ]] && [[ $TEMP_FLAG -eq 0 ]]; then
	MSG+="${AMBIENT_ENV}の室温が高いです。$TEMP deg C です。"
	export TEMP_FLAG=1
elif [[ $TEMP -lt 30 ]] && [[ $TEMP_FLAG -eq 1 ]]; then
	MSG+="${AMBIENT_ENV}の室温が$TEMP deg Cまで下がりました。"
	export TEMP_FLAG=0
fi

echo $CO2_FLAG > /dev/shm/logger_co2_flag
echo $TEMP_FLAG > /dev/shm/logger_temp_flag

echo $CO2 > /dev/shm/logger_co2
echo $TEMP > /dev/shm/logger_temp
echo $HUM > /dev/shm/logger_hum
date '+%Y-%m-%dT%H:%M:%S%z' > /dev/shm/logger_timestamp

if [[ ! $MSG = "" ]]; then
	curl -sSX POST --data-urlencode 'payload={"channel": "'"${SLACK_POST_CH}"'", "username": "'"${SLACK_POST_USERNAME}"'", "text": "'"${MSG}"'", "icon_emoji": "'"${SLACK_POST_EMOJI}"'"}' ${SLACK_WEBHOOK} > /dev/null &
fi
