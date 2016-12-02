# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from common import *

def message_in(server_obj, client, topic_list, payload_list):
    LOG.info("Received message of type %s"% payload_list[0])
    if payload_list[0] == SOUND_OFF:
        sound_off(client, payload_list[1])

def sound_off(mqtt, client):
    mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, client)),\
    " ".join((SOUND_OFF,SELF)))
