# Setup Python logging --------------------------------------------------------
import logging
from sys import argv
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.CRITICAL,format=FORMAT)
LOG = logging.getLogger(argv[0])

from protocol.common import *

def message_in(server_obj, client, payload_list):
    if payload_list[0] in GLOBAL_TYPES:
        LOG.info("Received message of type %s"% GLOBAL_TYPES[payload_list[0]])
    else:
        LOG.debug("Received message of unknown type")
        return

    if payload_list[0] == SOUND_OFF and len(payload_list) >= 2:
        sound_off(server_obj, client, payload_list[1])
    else:
        LOG.debug("Received message was too short.")


def sound_off(server_obj, mqtt, client):
    mqtt_publish(mqtt,
        "/".join((DEFAULT_ROOT_TOPIC, GLOBAL, client)),
        " ".join((SOUND_OFF,server_obj.self)))
