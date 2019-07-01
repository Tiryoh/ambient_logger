#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import time
import datetime
# sensor
import RPi.GPIO as GPIO
from co2_sensor.MHZ14A import MHZ14A
from dht11_sensor.dht11 import DHT11
# database
import ambient
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def get_co2_concentration(co2):
    tmp1 = 1
    tmp2 = 2
    while tmp1/tmp2 < 0.8 or tmp1/tmp2 > 1.2:
        tmp1 = co2.read()
        time.sleep(1)
        tmp2 = co2.read()
    return tmp1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id")
    parser.add_argument("--wkey")
    parser.add_argument("--firebase")
    parser.add_argument("--loop", "-l", type=int, default=0)
    args = parser.parse_args()
    channel_id = args.id
    write_key = args.wkey
    firebase_key = args.firebase
    loop = args.loop

    print("channel_id: {}, write_key:{}".format(channel_id, write_key))

    # initialize ambient.io settings
    if write_key is not None:
        am = ambient.Ambient(channel_id, write_key)

    # initialize firestore settings
    if firebase_key is not None:
        cred = credentials.Certificate(firebase_key)
        firebase_admin.initialize_app(cred)
        db = firestore.client()

    # initialize sensors
    co2 = MHZ14A("/dev/ttyS0")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    temp = DHT11(pin=17)

    while(1):
        try:
            # read co2 concentration data
            co2_data = get_co2_concentration(co2)
            # read temperature and humidity data
            temp_data = temp.read()
            while not temp_data.is_valid():
                time.sleep(1)
                temp_data = temp.read()

            # prepare data for ambient.io
            data = {
                u'd1': co2_data,
                u'd2': temp_data.temperature,
                u'd3': temp_data.humidity
            }

            # post data to ambient.io
            if write_key is not None:
                r = am.send(data)
                print("post data: ", data)
            else:
                print("ambient.io: ", data)

            # prepare data for firestore
            date = datetime.datetime.now()
            data = {
                u'timestamp': date.isoformat(),
                u'co2': co2_data,
                u'temperature': temp_data.temperature,
                u'humidity': temp_data.humidity
            }

            # post data to firestore
            if firebase_key is not None:
                doc_ref = db.collection(u'ambient').document(date.strftime('%s'))
                doc_ref.set(data)
            else:
                print("firestore: ", data)

            if loop:
                time.sleep(57)
            else:
                break

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            sys.exit(0)
        finally:
            r = ""
            data = ""


if __name__ == '__main__':
    main()
