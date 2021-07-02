
import paho.mqtt.client

import config
import state


def publish():

    if (config.SWDEBUG):
        print("--->Sending MQTT Packet<---")
    state.mqtt_client.publish("skyweather2/state", state.StateJSON)
