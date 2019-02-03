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
    from googlesearch import search 
except ImportError: 
    print("No module named 'google' found") 

led = LED(17)

PRINT_DEBUG_TO_TERMINAL = True

fromtimestamp = datetime.datetime.fromtimestamp

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()
HOST = "localhost"
PORT = 1883

INTENT_SEARCH_DATASHEET = 'hermes/intent/mm16356:demoSearchDatasheet'
USER_RANDOM_ANSWER = 'hermes/intent/mm16356:component'
INTENT_COMPONENT = 'hermes/intent/mm16356:userRandomAnswer'

CALCULATOR_TOPICS = [INTENT_SEARCH_DATASHEET,USER_RANDOM_ANSWER]

# Subscribe to message stream
def onConnect(client, userdata, flags, rc):
    for topic in CALCULATOR_TOPICS:
        mqtt_client.subscribe(topic)
        print("subscribed to a topic")
    print("got to on connect")


def onMessage(client, userdata, message):
    print("got to on message")
    data = json.loads(message.payload)
    sessionId = data['sessionId']
    if message.topic == INTENT_SEARCH_DATASHEET:
        print("got to on message.topic datahseet")
        ask(text='For which component?', customData=json.dumps({
        'wasIntent': INTENT_SEARCH_DATASHEET
        }))
    elif message.topic == INTENT_COMPONENT:
        #customData = parseCustomData(message)
       # print(customData['userInput'])
        #query = "filetype:pdf datasheet " + customData['userInput']
        query = "filetype:pdf datasheet " + "bc546"
        print("opening datasheet for bc546") #say("opening datasheet for bc546")
        for j in search(query, tld="co.uk", num=1, stop=1, pause=2): 
            print(j) 
            wb.open_new_tab(j)
#    session_id = parse_session_id(message)
#    say(response)
    

def onSessionStarted(client, data, message):
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


def say(text):
    mqtt_client.publish('hermes/dialogueManager/startSession', json.dumps({
        'init': {
            'type': 'notification',
            'text': text
        }
    }))


def ask(text, client='default', intentFilter=None, customData=''):
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
    say("System OK")
    print("Sound played")
    mqtt_client.loop_forever()