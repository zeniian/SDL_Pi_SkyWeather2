# handles updating the IT Sensor Dictionary
import datetime

import state


def buildITReading(DeviceID, ChannelID, Temperature, Humidity, BatteryOK, time):
    newchannel = {}
    newchannel["deviceID"] = DeviceID
    newchannel["channelID"] = ChannelID
    newchannel["temperature"] = Temperature
    newchannel["humidity"] = Humidity
    newchannel["batteryOK"] = BatteryOK
    newchannel["time"] = time
    state.IndoorTH.append(newchannel)


def addITReading(DeviceID, ChannelID, Temperature, Humidity, BatteryOK, Time):
    # check existing records, update if found
    if len(state.IndoorTH) > 0:
        for singleChannel in state.IndoorTH:
            if singleChannel["channelID"] == ChannelID:
                singleChannel["deviceID"] = DeviceID
                singleChannel["temperature"] = Temperature
                singleChannel["humidity"] = Humidity
                singleChannel["batteryOK"] = BatteryOK
                singleChannel["time"] = Time
                return
    buildITReading(DeviceID, ChannelID, Temperature, Humidity, BatteryOK, Time)
