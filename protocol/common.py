"""This file contains values that both the client and server require"""

DEFAULT_SERVER_PORT = 1883
DEFAULT_SERVER_URL = "iot.eclipse.org"

# GLOBAL MESSAGE TYPES
__SOUND_OFF =       '00'

# SERVER MESSAGE TYPES
__CONN_REQ =        '10'
__GAME_LIST_REQ =   '11'
__GAME_LIST =       '12'
__JOIN_GAME =       '13'
__CREATE_GAME =     '14'

# GAME MESSAGE TYPES
__GAME_SETUP =      '200'
__SHIP_POS =        '201'
__WAIT_FOR_START =  '202'
__START_GAME =      '203'
__PLAY_TURN =       '204'
__SHOOT =           '205'
__SPLASH =          '206'
__BOOM =            '207'
__SUNK =            '208'
__GAME_OVER =       '209'
__REPLAY_GAME =     '210'
__GAME_END =        '211'

#YEA AND NAY
_YEA = "YEA"
_NAY = "NAY"
