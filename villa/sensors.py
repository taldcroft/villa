#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# Modified by Tom Aldcroft, 2016.
# This code is released into the public domain

from __future__ import division

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

from .adafruit import BME280
from .adafruit import mcp3008

def get_status():
    # read the analog pin for ADC 0
    status = {}
    status['temp_adc0'] = mcp3008.get_adc_temperature(0)

    sensor280 = BME280.BME280(mode=BME280.BME280_OSAMPLE_8)

    status['temp_280'] = sensor280.read_temperature()
    status['humidity_280'] = sensor280.read_humidity()

    return status

if __name__ == '__main__':
    print(get_status())

