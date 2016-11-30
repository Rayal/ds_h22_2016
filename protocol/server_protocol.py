from common import *
import paho.mqtt.client as mqtt
import global_functions as gf

def message_in(client, userdata, msg):
    if not msg.topic.startswith(DEFAULT_ROOT_TOPIC + "/"):
        return
    topic = msg.topic[DEFAULT_ROOT_LEN:].split("/")
    if topic[0] in CATEGORIES:
        print "Received message from %s topic"%CATEGORIES[topic[0]]
        if topic[0] == GLOBAL:
            gf.message_in(client, topic[1:], msg.payload.split(" "))
    else:
        return


#def sound_off(client):
