#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import ambient
import sys
import time
import threading
import RPi.GPIO as GPIO
from co2_sensor.MHZ14A import MHZ14A
from dht11_sensor.dht11 import DHT11
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id")
    parser.add_argument("--wkey")
    parser.add_argument("--firebase")
    args = parser.parse_args()
    channel_id = args.id
    write_key = args.wkey
    firebase_key = args.firebase

    print("channel_id: {}, write_key:{}".format(channel_id, write_key))

    if write_key is not None:
        am = ambient.Ambient(channel_id, write_key)

    # initialize firebase
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
            tmp1 = 1
            tmp2 = 2
            while tmp1/tmp2 < 0.8 or tmp1/tmp2 > 1.2:
                tmp1 = co2.read()
                time.sleep(1)
                tmp2 = co2.read()
                co2_data = tmp1
            # read temperature and humidity data
            temp_data = temp.read()
            while not temp_data.is_valid():
                time.sleep(1)
                temp_data = temp.read()
            # data = co2_data
            # data['temperature'] = temp_data.temperature
            # data['humidity'] = temp_data.humidity
            data = {}
            data['d1'] = co2_data
            data['d2'] = temp_data.temperature
            data['d3'] = temp_data.humidity

            date = datetime.datetime.now()

            if firebase_key is not None:
                doc_ref = db.collection(u'ambient').document(date.strftime('%s'))
                doc_ref.set({
                    u'timestamp': date.isoformat(),
                    u'co2': data['d1'],
                    u'temperature': data['d2'],
                    u'humidity': data['d3']
                })

            if write_key is not None:
                r = am.send(data)
                print("post data: ", data)
            else:
                print("data: ", data)

            time.sleep(57)

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            sys.exit(0)
        except:
            print(data, end="")
            print(type(data), end="")
            print(r)
        finally:
            r = ""
            data = ""


if __name__ == '__main__':
    main()
