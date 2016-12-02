from common import *
import global_functions as wf
import server_functions as sf

def message_in(client, userdata, msg):
    if not msg.topic.startswith(DEFAULT_ROOT_TOPIC + "/"):
        return
    topic = msg.topic[DEFAULT_ROOT_LEN:].split("/")
    if topic[0] in CATEGORIES:
        print "Received message from %s topic"%CATEGORIES[topic[0]]
        if topic[0] == GLOBAL:
            wf.message_in(client, topic[1:], msg.payload.split(" "))
        elif topic[0] == SERVER:
            sf.message_in(client, topic[1:], msg.payload.split(" "))


#def sound_off(client):
