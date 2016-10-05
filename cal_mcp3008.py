#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

from __future__ import division

from math import log
import time
import os
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as dates
from astropy.time import Time
import astropy.units as u
from matplotlib.dates import DateFormatter
import Adafruit_BME280 as bme280

sensor280 = bme280.BME280(mode=bme280.BME280_OSAMPLE_8)

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# resistance at 25 degrees C
THERMISTORNOMINAL = 10000      
# // temp. for nominal resistance (almost always 25 C)
TEMPERATURENOMINAL= 25   
# // how many samples to take and average, more takes longer
# // but is more 'smooth'
#define NUMSAMPLES 5
# // The beta coefficient of the thermistor (usually 3000-4000)
BCOEFFICIENT = 3950
# // the value of the 'other' resistor
SERIESRESISTOR = 10000    

TIMELENGTH = 50
YMIN = 20
YMAX = 30
plt.ion()
fig = plt.figure(figsize=(18,6))
ax = fig.add_subplot(111)
plt.ylim(YMIN, YMAX)

times = [Time.now().plot_date, (Time.now() + TIMELENGTH*u.s).plot_date]
steinharts = [25., 25.]
degrees280s = [25., 25.]
humidity280s = [0., 0]

hl = ax.plot_date(times, steinharts)[0]
hl2 = ax.plot_date(times, steinharts)[0]
plt.title('Sensor temperature')
plt.ylabel('Degrees (C)')
plt.grid()

ax2 = ax.twinx()
ax2.set_ylim(0, 100)
hl3 = ax2.plot_date(times, humidity280s, 'r*')[0]

hms_formatter = DateFormatter('%H:%M:%S')
ax.xaxis.set_major_formatter(hms_formatter)


# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
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
        return adcout

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

# 10k trim pot connected to adc #0
potentiometer_adc = 0;

last_read = 0       # this keeps track of the last potentiometer value
tolerance = 5       # to keep from being jittery we'll only change
                    # volume when the pot has moved more than 5 'counts'
while True:
    # read the analog pin
    counts = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    print('Counts = {}'.format(counts))

    average = 1023 / counts - 1
    average = SERIESRESISTOR / average
    # Serial.print("Thermistor resistance ") 
    # Serial.println(average)
 
    steinhart = average / THERMISTORNOMINAL     # (R/Ro)
    steinhart = log(steinhart)                  # ln(R/Ro)
    steinhart /= BCOEFFICIENT                   # 1/B * ln(R/Ro)
    steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15) # + (1/To)
    steinhart = 1.0 / steinhart                 # Invert
    steinhart -= 273.15                         # convert to C
 
    print("ADC Temperature = {:.2f}".format(steinhart))

    degrees280 = sensor280.read_temperature()
    humidity280 = sensor280.read_humidity()

    # hang out and do nothing for a half second
    time.sleep(0.5)

    times.append(Time.now().plot_date)
    steinharts.append(steinhart)
    degrees280s.append(degrees280)
    humidity280s.append(humidity280)

    if len(steinharts) > TIMELENGTH:
        steinharts = steinharts[-TIMELENGTH:]
        degrees280s = degrees280s[-TIMELENGTH:]
        humidity280s = humidity280s[-TIMELENGTH:]
        times = times[-TIMELENGTH:]

    ymin = np.min(steinharts)
    ymax = np.max(steinharts)
    ymin = min(ymin,YMIN)
    ymax = max(ymax,YMAX)

    hl.set_ydata(steinharts)
    hl.set_xdata(times)

    hl2.set_ydata(degrees280s)
    hl2.set_xdata(times)

    hl3.set_ydata(humidity280s)
    hl3.set_xdata(times)

    ax.set_ylim(ymin,ymax)
    ax.set_xlim(np.min(times), np.max(times))

    fig.canvas.draw()
    fig.canvas.flush_events()
