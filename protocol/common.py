"""This file contains values that both the client and server require"""

from os import getpid, name

DEFAULT_SERVER_PORT = 1883
DEFAULT_SERVER_URL = "iot.eclipse.org"
DEFAULT_ROOT_TOPIC = "DS2016_BATTLESHIP"
DEFAULT_ROOT_LEN = len(DEFAULT_ROOT_TOPIC) + 1

SELF = name + str(getpid())

# GLOBAL MESSAGE TYPES
SOUND_OFF =       '00'

# SERVER MESSAGE TYPES
CONN_REQ =        '10'
GAME_LIST_REQ =   '11'
GAME_LIST =       '12'
JOIN_GAME =       '13'
CREATE_GAME =     '14'

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
