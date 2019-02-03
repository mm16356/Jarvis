# encoding: utf-8
from __future__ import unicode_literals

import datetime
import json

import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqttPublish

import requests

PRINT_DEBUG_TO_TERMINAL = True

fromtimestamp = datetime.datetime.fromtimestamp

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()
HOST = "localhost"
PORT = 1883

CALCULATOR_TOPICS = ['hermes/intent/mm16356:ComputeSum']

# Subscribe to msg stream
def onConnect(client, userdata, flags, rc):
    for topic in CALCULATOR_TOPICS:
        mqtt_client.subscribe(topic)
        print("subscribed to a topic")
    print("got to on connect")


def onMessage(client, userdata, msg):
    print("got to on message")

    
    if msg.topic not in CALCULATOR_TOPICS:
        return
        
    slots = parse_slots(msg)
    sum = addTwo(slots)
    
    #say(session_id, "Hello")
    
    if msg.topic == 'hermes/intent/mm16356:ComputeSum':
        response = ("The sum is {0}.".format(sum["sum"]))
        
    session_id = parse_session_id(msg)
    say(response)


def addTwo(slots):
    '''
    parse numeber slots and add
    '''
    number1 = slots.get("FirstTerm", None)
    number2 = slots.get("SecondTerm", None)
    sum = number1 + number2
    return {"sum": sum}


def say(session_id, text):
    '''
    Prints the output text (if debig) to the console and TTS engine
    '''
    if PRINT_DEBUG_TO_TERMINAL:
        print(text)
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'text': text, "sessionId" : session_id}))


def parse_session_id(msg): 
    '''
    Extract the session id from the message
    '''
    data = json.loads(msg.payload)
    return data['sessionId']

def parse_slots(msg):
    '''
    We extract the slots as a dict
    '''
    data = json.loads(msg.payload)
    return {slot['slotName']: slot['rawValue'] for slot in data['slots']}    
    
    
def say(text):
    mqtt_client.publish('hermes/dialogueManager/startSession', json.dumps({'init': {'type': 'notification','text': text}}))
    

if __name__ == '__main__':
    mqtt_client.on_connect = onConnect
    mqtt_client.on_message = onMessage
    mqtt_client.connect(HOST, PORT)
    print("Demo loaded")
    say("This is Jarvis. What do you want?")
    print("Sound played")
    mqtt_client.connect(HOST, PORT)
    mqtt_client.loop_forever()