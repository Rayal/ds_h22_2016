FIND_SERVERS =      1
CONNECT_SERVER =    2
SERVER_CONNECTED =  3
GAME_CONFIG =       4
SET_SHIPS =         5
GAME_STARTED =      6
PLAYING =           7

states = {
    FIND_SERVERS:       'Find Servers',
    CONNECT_SERVER:     'Connect to Server',
    SERVER_CONNECTED:   'Connected to server',
    GAME_CONFIG:        'Send game configuration',
    SET_SHIPS:          'Set ship positions',
    GAME_STARTED:       'Connected to a running game',
    PLAYING:            'Start playing'
}

RET_OK =        100
RET_ALT =       200
RET_NOK =       300
RET_RETRY =     400
RET_WAIT =      500
RET_TIMEOUT =   600

state_ret = {
    RET_OK:         'OK',
    RET_ALT:        'Alternative OK',
    RET_NOK:        'NOK',
    RET_RETRY:      'Retry',
    RET_WAIT:       'Wait',
    RET_TIMEOUT:    'Timeout'
}

state_transitions = {
    (RET_OK,        FIND_SERVERS):          CONNECT_SERVER,
    #(RET_NOK,       FIND_SERVERS):          FIND_SERVERS,
    (RET_RETRY,     FIND_SERVERS):          FIND_SERVERS,
    (RET_OK,        CONNECT_SERVER):        SERVER_CONNECTED,
    (RET_NOK,       CONNECT_SERVER):        FIND_SERVERS,
    #(RET_RETRY,     CONNECT_SERVER):        CONNECT_SERVER,
    #(RET_WAIT,      CONNECT_SERVER):        CONNECT_SERVER,
    (RET_TIMEOUT,   CONNECT_SERVER):        FIND_SERVERS,
    (RET_OK,        SERVER_CONNECTED):      SET_SHIPS,
    (RET_ALT,       SERVER_CONNECTED):      GAME_CONFIG,
    (RET_NOK,       SERVER_CONNECTED):      FIND_SERVERS,
    (RET_RETRY,     SERVER_CONNECTED):      SERVER_CONNECTED,
    (RET_WAIT,      SERVER_CONNECTED):      SERVER_CONNECTED,
    (RET_TIMEOUT,   SERVER_CONNECTED):      SERVER_CONNECTED,
    (RET_OK,        GAME_CONFIG):           SET_SHIPS,
    (RET_RETRY,     GAME_CONFIG):           GAME_CONFIG,
    (RET_OK,        SET_SHIPS):             GAME_STARTED,
    (RET_NOK,       SET_SHIPS):             SET_SHIPS,
    (RET_OK,        GAME_STARTED):          PLAYING,
    (RET_NOK,       GAME_STARTED):          SET_SHIPS,
    (RET_RETRY,     GAME_STARTED):          GAME_STARTED,
    (RET_WAIT,      GAME_STARTED):          GAME_STARTED,
    (RET_TIMEOUT,   GAME_STARTED):          GAME_STARTED,
    (RET_OK,        PLAYING):               PLAYING,
    (RET_NOK,       PLAYING):               PLAYING,
    (RET_RETRY,     PLAYING):               PLAYING,
    (RET_WAIT,      PLAYING):               PLAYING,
    (RET_TIMEOUT,   PLAYING):               PLAYING
}
