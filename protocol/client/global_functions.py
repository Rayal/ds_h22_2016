# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *

def message_in(client_obj, client, topic_list, payload_list):
    LOG.info("Received message of type %s"% payload_list[0])
    LOG.debug ("Message: %s - %s"%("/".join(topic_list), " ".join(payload_list)))
    if payload_list[0] == SOUND_OFF:
        sound_off(client, payload_list[1])

def sound_off(mqtt, client):
    print("Servers online: %s" %client)
    #mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, client)),\
    #" ".join((SOUND_OFF,SELF)))
