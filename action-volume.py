#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import random

CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

ACK = ["Trait bien", "OK", "daccord", "sait fait", "Pas de problaime", "entendu"]

class Volume(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """
    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None


        # start listening to MQTT
        self.start_blocking()

    # --> Sub callback function, one per intent
    def setVolumeCallback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)

        volume = 5

        if intent_message.slots.volume:
            volume = intent_message.slots.volume.first().value

        print "Volume: " + str(volume)

        publish.single('hermes/volume/set', payload=json.dumps({'siteId': intent_message.site_id, 'volume': volume}), hostname=MQTT_IP_ADDR, port=MQTT_PORT)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, ACK[random.randint(0,len(ACK) - 1)], "")

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):

        intent_name = intent_message.intent.intent_name
        if ':' in intent_name:
            intent_name = intent_name.split(":")[1]
        if intent_name == 'setVolume':
            self.setVolumeCallback(hermes, intent_message)

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Volume()