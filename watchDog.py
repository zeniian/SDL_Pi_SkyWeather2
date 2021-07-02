from __future__ import print_function

import time

import RPi.GPIO as GPIO

import config

# WatchDog Programs
GPIO.setwarnings(False)


def patTheDog():

    # pat the dog
    if (config.SWDEBUG):
        print("------Patting The Dog------- ")

    GPIO.setup(config.WATCHDOGTRIGGER, GPIO.OUT)
    GPIO.output(config.WATCHDOGTRIGGER, False)
    time.sleep(0.2)
    GPIO.output(config.WATCHDOGTRIGGER, True)
    GPIO.setup(config.WATCHDOGTRIGGER, GPIO.IN)
