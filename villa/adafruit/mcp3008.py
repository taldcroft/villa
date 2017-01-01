#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

import time
import os
from math import log

from ..util import degC2degF
import RPi.GPIO as GPIO

DEBUG = 1

# resistance at 25 degrees C
THERMISTORNOMINAL = 10000  # temp. for nominal resistance (almost always 25 C)
TEMPERATURENOMINAL= 25 # how many samples to take and average, more takes longer
                       # but is more 'smooth'
BCOEFFICIENT = 3950 # The beta coefficient of the thermistor (usually 3000-4000)
                    # // the value of the 'other' resistor
SERIESRESISTOR = 10000    

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)


def get_adc_temperature(adcnum,
                        clockpin=SPICLK, 
                        mosipin=SPIMOSI, 
                        misopin=SPIMISO, 
                        cspin=SPICS):
    """
    Read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    """
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)
    
    adcout >>= 1       # first bit is 'null' so drop it

    average = 1023 / adcout - 1
    try:
        average = SERIESRESISTOR / average
    except Exception as err:
        print('divide by zero {}'.format(average))
        average = 1.0
 
    steinhart = average / THERMISTORNOMINAL     # (R/Ro)
    steinhart = log(steinhart)                  # ln(R/Ro)
    steinhart /= BCOEFFICIENT                   # 1/B * ln(R/Ro)
    steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15) # + (1/To)
    steinhart = 1.0 / steinhart                 # Invert
    steinhart -= 273.15                         # convert to C
 
    return degC2degF(steinhart)  # output in F
