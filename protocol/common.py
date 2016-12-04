"""This file contains values that both the client and server require"""

# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()


from os import getpid, name

DEFAULT_SERVER_PORT = 1883
DEFAULT_SERVER_URL = "iot.eclipse.org"
DEFAULT_ROOT_TOPIC = "DS2016_BATTLESHIP"
DEFAULT_ROOT_LEN = len(DEFAULT_ROOT_TOPIC) + 1

SELF = name + str(getpid())

# GLOBAL MESSAGE TYPES
SOUND_OFF =       '00'
GLOBAL_TYPES = {
    SOUND_OFF: "SOUND_OFF"
}

# SERVER MESSAGE TYPES
CONN_REQ =        '10'
GAME_LIST_REQ =   '11'
GAME_LIST =       '12'
JOIN_GAME =       '13'
CREATE_GAME =     '14'
DISCONNECT =      '15'
SERVER_TYPES = {
    CONN_REQ:       "CONN_REQ",
    GAME_LIST_REQ:  "GAME_LIST_REQ",
    GAME_LIST:      "GAME_LIST",
    JOIN_GAME:      "JOIN_GAME",
    CREATE_GAME:    "CREATE_GAME",
    DISCONNECT:     "DISCONNECT"
}

# GAME MESSAGE TYPES
GAME_SETUP =      '200'
SHIP_POS =        '201'
WAIT_FOR_START =  '202'
START_GAME =      '203'
PLAY_TURN =       '204'
SHOOT =           '205'
SPLASH =          '206'
BOOM =            '207'
SUNK =            '208'
GAME_OVER =       '209'
REPLAY_GAME =     '210'
GAME_END =        '211'
DISCONNECT =      '212'
GAME_TYPES = {
    GAME_SETUP:     "GAME_SETUP",
    SHIP_POS:       "SHIP_POS",
    WAIT_FOR_START: "WAIT_FOR_START",
    START_GAME:     "START_GAME",
    PLAY_TURN:      "PLAY_TURN",
    SHOOT:          "SHOOT",
    SPLASH:         "SPLASH",
    BOOM:           "BOOM",
    SUNK:           "SUNK",
    GAME_OVER:      "GAME_OVER",
    REPLAY_GAME:    "REPLAY_GAME",
    GAME_END:       "GAME_END",
    DISCONNECT:     "DISCONNECT"
}

#YEA AND NAY
YEA = "YEA"
NAY = "NAY"

#TOPICS
GLOBAL =  "G"
SERVER =  "S"
GAME =    "P"
CATEGORIES = {  GLOBAL:   "GLOBAL",
                SERVER:   "SERVER",
                GAME:     "GAME"
}

#SEPARATORS
OBJ_SEP =       chr(30)
SUB_OBY_SEP =   chr(31)


def mqtt_publish(mqtt_client, topic, payload = None, retain = False):
    LOG.debug("Sending: %s - %s" % (topic, payload))
    mqtt_client.publish(topic, payload, retain = retain)
