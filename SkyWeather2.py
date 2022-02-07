#!/usr/bin/env python3
#
# SkyWeather2 Solar Powered Weather Station
# November 2020
#
# SwitchDoc Labs
# www.switchdoc.com
#


import datetime
import platform
import subprocess
import sys
import time

import apscheduler.events
import paho.mqtt.client as mqtt
from apscheduler.schedulers.background import BackgroundScheduler

import config
import DustSensor
import pclogging
import publishMQTT
import sendemail
import state
import updateBlynk
import util
import watchDog
import wiredSensors
import wirelessSensors
from bmp280 import BMP280

config.SWVERSION = "027.3"

# Scheduler Helpers

# print out faults inside events


def ap_my_listener(event):
    if event.exception:
        print(event.exception)
        print(event.traceback)


# Program Requirement Checking

if (config.enable_MySQL_Logging):
    # Check for updates having been applied
    try:
        con = util.weatherSenseConnect()
        cur = con.cursor()
        query = "SELECT * FROM AS433MHZ"
        cur.execute(query)
        cur.close()
        con.close()
    except:
        # print(traceback.format_exc())
        print("--------")
        print("MySQL Database WeatherSenseWireless Updates Not Installed.")
        print("Run this command on your MySQL server:")
        print("sudo mysql -u root -p WeatherSenseWireless < updateWeatherSenseWireless.sql")
        print("SkyWeather2 Stopped")
        print("--------")
        sys.exit("SkyWeather2 Requirements Error Exit")



# main program
print("")

print("##########################################################")
print("SkyWeather2 Weather Station Version " +
      config.SWVERSION+" - SwitchDoc Labs")
print("")
print("Program Started at:" + time.strftime("%Y-%m-%d %H:%M:%S"))
print("##########################################################")
print("")

# detect devices

################
# Dust Sensor
################

try:

    DustSensor.powerOnDustSensor()
    time.sleep(3)
    myData = DustSensor.get_data()
    #print ("data=",myData)

    config.DustSensor_Present = True

except:

    config.DustSensor_Present = False


################
# BMP280 Setup
################

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


# Initialise the BMP280
bus = SMBus(1)

try:
    bmp280 = BMP280(i2c_dev=bus, i2c_addr=0x77)
    state.BarometricTemperature = round(bmp280.get_temperature(), 2)

    config.BMP280_Present = True
except:
    if (config.SWDEBUG):
        pass
        # print(traceback.format_exc())

    config.BMP280_Present = False

################
# SkyCamera Setup
################

if (platform.machine() == 'aarch64'):
    print("SkyCamera setup skipped.")
    print("picamera not supported on aarch64: https://github.com/raspberrypi/Raspberry-Pi-OS-64bit/issues/86")
    config.Camera_Present = False
else:
    import picamera

    import SkyCamera

    # Establish WeatherSTEMHash
    if (config.USEWEATHERSTEM == True):
        state.WeatherSTEMHash = SkyCamera.SkyWeatherKeyGeneration(
            config.STATIONKEY)

    # Detect Camera WeatherSTEMHash
    try:

        with picamera.PiCamera() as cam:
            if (config.SWDEBUG):
                print("Pi Camera Revision", cam.revision)
            cam.close()
        config.Camera_Present = True
    except:
        config.Camera_Present = False


# display device present variables


print("----------------------")
print(util.returnStatusLine("BMP280", config.BMP280_Present))
print(util.returnStatusLine("SkyCam", config.Camera_Present))
print(util.returnStatusLine("OLED", config.OLED_Present))
print(util.returnStatusLine("SunAirPlus/SunControl", config.SunAirPlus_Present))
print(util.returnStatusLine("SolarMAX", config.SolarMAX_Present))
print(util.returnStatusLine("DustSensor", config.DustSensor_Present))
print()
print(util.returnStatusEnable("UseBlynk", config.USEBLYNK))
print(util.returnStatusEnable("UseWSLIGHTNING", config.USEWSLIGHTNING))
print(util.returnStatusEnable("UseWSAQI", config.USEWSAQI))
print(util.returnStatusEnable("UseWSSKYCAM", config.USEWSSKYCAM))
print(util.returnStatusEnable("UseMySQL", config.enable_MySQL_Logging))
print(util.returnStatusEnable("UseMQTT", config.MQTT_Enable))
print(util.returnStatusLine("Check WLAN", config.enable_WLAN_Detection))
print(util.returnStatusLine("WeatherUnderground", config.WeatherUnderground_Present))
print(util.returnStatusLine("UseWeatherStem", config.USEWEATHERSTEM))

print("----------------------")

# startup


pclogging.systemlog(
    config.INFO, "SkyWeather2 Startup Version "+config.SWVERSION)

if (config.USEBLYNK):
    updateBlynk.blynkEventUpdate("SW Startup Version "+config.SWVERSION)
    updateBlynk.blynkTerminalUpdate("SW Startup Version "+config.SWVERSION)

subjectText = "The " + config.STATIONKEY + \
    " SkyWeather2 Raspberry Pi has #rebooted."
ipAddress = subprocess.check_output(['hostname',  '-I'])
bodyText = "SkyWeather2 Version "+config.SWVERSION + \
    " Startup \n"+ipAddress.decode()+"\n"
if (config.SunAirPlus_Present):
    sampleSunAirPlus()
    bodyText = bodyText + "\n" + "BV=%0.2fV/BC=%0.2fmA/SV=%0.2fV/SC=%0.2fmA" % (
        state.batteryVoltage, state.batteryCurrent, state.solarVoltage, state.solarCurrent)

sendemail.sendEmail("test", bodyText, subjectText,
                    config.notifyAddress,  config.fromAddress, "")


if (config.USEBLYNK):
    updateBlynk.blynkInit()


# set up MQTT
if (config.MQTT_Enable):
    state.mqtt_client = mqtt.Client(client_id="SkyWeather2")
    state.mqtt_client.connect(config.MQTT_Server_URL,
                              port=config.MQTT_Port_Number)


# Set up scheduler

scheduler = BackgroundScheduler()

# for debugging
scheduler.add_listener(ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)

##############
# setup tasks
##############
hdc1080 = None
wiredSensors.readWiredSensors(bmp280, hdc1080)


def tick():
    print('Tick! The time is: %s' % datetime.datetime.now())


# prints out the date and time to console
scheduler.add_job(tick, 'interval', seconds=60)

# read wireless sensor package
scheduler.add_job(wirelessSensors.readSensors)  # run in background

# read wired sensor package
scheduler.add_job(wiredSensors.readWiredSensors, 'interval',
                  args=[bmp280, hdc1080], seconds=30)

if (config.SWDEBUG):
    # print state
    scheduler.add_job(state.printState, 'interval', seconds=60)

if (config.USEBLYNK):
    scheduler.add_job(updateBlynk.blynkStateUpdate, 'interval', seconds=30)

if (config.MQTT_Enable):
    scheduler.add_job(publishMQTT.publish, 'interval',
                      seconds=config.MQTT_Send_Seconds)

scheduler.add_job(watchDog.patTheDog, 'interval',
                  seconds=20)   # reset the WatchDog Timer


# every 5 days at 00:04, reboot
#scheduler.add_job(rebootPi, 'cron', day='5-30/5', hour=0, minute=4, args=["5 day Reboot"])

# check for Barometric Trend (every 15 minutes)
scheduler.add_job(util.barometricTrend, 'interval', seconds=15*60)

if (config.DustSensor_Present):
    # DustSensor.read_AQI() # get current value
    scheduler.add_job(DustSensor.read_AQI, 'interval', seconds=60*5)

if (config.USEWSAQI):
    wirelessSensors.WSread_AQI()  # get current value
    scheduler.add_job(wirelessSensors.WSread_AQI, 'interval', seconds=60*20)


# weather sensors

scheduler.add_job(pclogging.writeWeatherRecord, 'interval', seconds=2*60)
scheduler.add_job(pclogging.writeITWeatherRecord, 'interval', seconds=2*60)


# sky camera
if (config.USEWEATHERSTEM):
    if (config.Camera_Present):
        scheduler.add_job(SkyCamera.takeSkyPicture, 'interval',
                          seconds=config.INTERVAL_CAM_PICS__SECONDS)


# start scheduler
scheduler.start()
print("-----------------")
print("Scheduled Jobs")
print("-----------------")
scheduler.print_jobs()
print("-----------------")


def killLogger():
    scheduler.shutdown()
    print("Scheduler Shutdown....")
    exit()


# Main Loop
while True:
    time.sleep(1.0)
