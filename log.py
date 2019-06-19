#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time
import sys
import ambient
from co2_sensor.MHZ14A import MHZ14A
from dht11_sensor.dht11 import DHT11
import RPi.GPIO as GPIO


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--id")
    parser.add_argument("--wkey")
    args = parser.parse_args()
    channel_id = args.id
    write_key = args.wkey

    print("channel_id: {}, write_key:{}".format(channel_id, write_key))

    if write_key != None:
        am = ambient.Ambient(channel_id, write_key)

    co2 = MHZ14A("/dev/ttyS0")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    temp = DHT11(pin=17)

    while(1):
        try:
            co2_data = co2.get()
            temp_data = temp.read()
            while not temp_data.is_valid():
                time.sleep(1)
                temp_data = temp.read()
            #data = co2_data
            #data['temperature'] = temp_data.temperature
            #data['humidity'] = temp_data.humidity
            data = {}
            data['d1'] = co2_data['ppm']
            data['d2'] = temp_data.temperature
            data['d3'] = temp_data.humidity
            if write_key != None:
                r = am.send(data)
                print("post data: ", data)
            else:
                print("data: ", data)
            time.sleep(58)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            co2.close()
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
