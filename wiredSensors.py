from __future__ import division, print_function

import datetime
import sys
import traceback

from past.utils import old_div

import buildJSON
import config
import state

#
# wired sensor routines


def readWiredSensors(bmp280, hdc1080):

    # read wired sensors

    if (config.BMP280_Present):
        try:
            state.BarometricTemperature = round(bmp280.get_temperature(), 2)
            state.BarometricPressure = round(
                old_div(bmp280.get_pressure(), 1000)*100, 5)
            #state.Altitude = round(bmp280.get_altitude(), 4)
            state.Altitude = config.BMP280_Altitude_Meters
            state.BarometricPressureSeaLevel = round(old_div(
                bmp280.get_sealevel_pressure(config.BMP280_Altitude_Meters), 1000)*100, 5)
        except:
            if (config.SWDEBUG):
                print(traceback.format_exc())
                print(
                    ("readWiredSensors Unexpected error:", sys.exc_info()[0]))

    #print("Looking for buildJSONSemaphore Acquire")
    state.buildJSONSemaphore.acquire()
    #print("buildJSONSemaphore Acquired")
    state.StateJSON = buildJSON.getStateJSON()
    # if (config.SWDEBUG):
    #    print("currentJSON = ", state.StateJSON)
    state.buildJSONSemaphore.release()
    #print("buildJSONSemaphore Released")
