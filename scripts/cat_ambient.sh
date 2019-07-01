#!/usr/bin/env bash
set -eu
echo "co2:"
cat /dev/shm/logger_co2
echo "temp:"
cat /dev/shm/logger_temp
echo "hum:"
cat /dev/shm/logger_hum
