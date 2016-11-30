from common import *

def message_in(client, topic_list, payload_list):
    print "Received message of type %s"% payload_list[0]
    if payload_list[0] == SOUND_OFF:
        sound_off(client, payload_list[1])

def sound_off(mqtt, client):
    mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, client)),\
    " ".join((SOUND_OFF,SELF)))
