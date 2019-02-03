# encoding: utf-8
from __future__ import unicode_literals

import datetime
import json

import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqttPublish

import requests

from gpiozero import LED
from time import sleep

import webbrowser as wb

try: 
    from googlesearch import search as schh
except ImportError: 
    print("No module named 'google' found") 

pin1 = LED(17)
pin2 = LED(27)
pin3 = LED(22)

PRINT_DEBUG_TO_TERMINAL = True

fromtimestamp = datetime.datetime.fromtimestamp

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()
HOST = "localhost"
PORT = 1883

INTENT_SEARCH_DATASHEET = 'hermes/intent/mm16356:demoSearchDatasheet'
INTENT_COMPONENT = 'hermes/intent/mm16356:component'
USER_RANDOM_ANSWER = 'hermes/intent/mm16356:userRandomAnswer'

CALCULATOR_TOPICS = [INTENT_SEARCH_DATASHEET,USER_RANDOM_ANSWER,INTENT_COMPONENT]

# Subscribe to message stream
def onConnect(client, userdata, flags, rc):
    for topic in CALCULATOR_TOPICS:
        mqtt_client.subscribe(topic)
        print("subscribed to a topic")
    print("got to on connect")
    pin1.on()
    pin2.on()
    pin3.on()


def onMessage(client, userdata, message):
    print("got to on message")
    data = json.loads(message.payload)
    sessionId = data['sessionId']
    if message.topic == INTENT_SEARCH_DATASHEET:
        pin1.on()
        pin2.off()
        pin3.on()
        print("got to on message.topic datahseet")
        ask(text='For which component?', customData=json.dumps({
        'wasIntent': INTENT_SEARCH_DATASHEET
        }))
    elif message.topic == INTENT_COMPONENT:
        pin1.on()
        pin2.off()
        pin3.on()
        #customData = parseCustomData(message)
       # print(customData['userInput'])
        #query = "filetype:pdf datasheet " + customData['userInput']
        query = "datasheet bc546"
        say("opening data sheet for b c 5 4 6")

        for j in schh(query, tld="co.uk", num=1, stop=1, pause=1): 
            print(j) 
            wb.open_new_tab(j)
        print("opening datasheet for bc546") 
#    session_id = parse_session_id(message)
#    say(response)
    

def onSessionStarted(client, data, message):
    pin1.on()
    pin2.on()
    pin3.off()
    print("got to onSessionStarted")
    sessionId = parseSessionId(message)
    sessions[sessionId] = message


def onSessionEnded(client, data, message):
    print("got to onSessionEnded")
    sessionId = parseSessionId(message)
    if sessionId in sessions:
        del sessions[sessionId]

def onIntentNotRecognized(client, data, message):
    print("got to onIntentNotRecognized")
    payload = json.loads(message.payload)
    sessionId = parseSessionId(message)

    wasMessage = sessions[sessionId]
    customData = parseCustomData(wasMessage)

    # This is not a continued session as there's no custom data
    if customData is None:
        return

    siteId = parseSiteId(wasMessage)

    customData['userInput'] = payload['input']
    payload['customData'] = customData

    payload['siteId'] = siteId
    wasMessage.payload = json.dumps(payload)
    wasMessage.topic = 'userRandomAnswer'

    onMessage(None, None, wasMessage)

def endTalk(sessionId, text):
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({
        'sessionId': sessionId,
        'text': text
    }))
    pin1.on()
    pin2.on()
    pin3.on()


def say(text):
    pin1.on()
    pin2.off()
    pin3.off()
    mqtt_client.publish('hermes/dialogueManager/startSession', json.dumps({
        'init': {
            'type': 'notification',
            'text': text
        }
    }))



def ask(text, client='default', intentFilter=None, customData=''):
    pin1.on()
    pin2.off()
    pin3.off()
    mqtt_client.publish('hermes/dialogueManager/startSession', json.dumps({
        'siteId': client,
        'customData': customData,
        'init': {
            'type': 'action',
            'text': text,
            'canBeEnqueued': True
        }
    }))



def parseSessionId(message):
    data = json.loads(message.payload)
    if 'sessionId' in data:
        return data['sessionId']
    else:
        return False

def parseCustomData(message):
    data = json.loads(message.payload)
    if 'customData' in data and data['customData'] is not None:
        return json.loads(data['customData'])
    else:
        return None


def parseSiteId(message):
    data = json.loads(message.payload)
    if 'siteId' in data:
        return data['siteId']
    else:
        return 'default'

if __name__ == '__main__':
    mqtt_client.on_connect = onConnect
    mqtt_client.on_message = onMessage
    mqtt_client.message_callback_add("hermes/nlu/intentNotRecognized", onIntentNotRecognized)
    mqtt_client.message_callback_add('hermes/dialogueManager/sessionEnded', onSessionEnded)
    mqtt_client.message_callback_add('hermes/dialogueManager/sessionStarted', onSessionStarted)
    mqtt_client.connect(HOST, PORT)
    print("Demo loaded")
    print("Sound played")
    mqtt_client.loop_forever()