#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# Modified by Tom Aldcroft, 2016.
# This code is released into the public domain

from __future__ import division

from .adafruit import BME280
from .adafruit import mcp3008

def get_sensors():
    # read the analog pin for ADC 0
    sensors = {}

    sensors['temp_adc0'] = mcp3008.get_adc_temperature(0)

    sensor280 = BME280.BME280(mode=BME280.BME280_OSAMPLE_8)
    sensors['temp_280'] = sensor280.read_temperature()
    sensors['humidity_280'] = sensor280.read_humidity()

    return sensors

if __name__ == '__main__':
    print(get_sensors())

