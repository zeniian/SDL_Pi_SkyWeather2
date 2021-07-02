#!/usr/bin/env python3
# test HM3301 Laser Dust Sensor

import subprocess
import sys
import time
import traceback

import pigpio
import RPi.GPIO as GPIO

import config
import DustSensor
import SDL_Pi_HM3301

sys.path.append('./SDL_Pi_HM3301')


GPIO.setmode(GPIO.BCM)

GPIO.setup(config.DustSensorPowerPin, GPIO.OUT)
GPIO.output(config.DustSensorPowerPin, True)

#
if (config.SWDEBUG):
    print("Starting pigpio daemon")

# kill all pigpio instances
try:
    cmd = ['killall', 'pigpiod']
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    print(output)
    time.sleep(5)
except:
    # print(traceback.format_exc())
    pass

cmd = ['/usr/bin/pigpiod']
output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
print(output)

time.sleep(0.01)
try:
    while 1:

        DustSensor.powerOnDustSensor()
        time.sleep(3)
        myData = DustSensor.get_data()
        print("data=", myData)
        myAQI = DustSensor.get_aqi()
        DustSensor.print_data()
        print("AQI=", myAQI)
        DustSensor.powerOffDustSensor()

        time.sleep(3)

except:
    # DustSensor.powerOffDustSensor()
    print(traceback.format_exc())
