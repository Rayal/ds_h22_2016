FIND_SERVERS =      1
CONNECT_SERVER =    2
SERVER_CONNECTED =  3
GAME_STARTED =      4

states = {
    FIND_SERVERS:       'Find Servers',
    CONNECT_SERVER:     'Connect to Server',
    SERVER_CONNECTED:   'Connected to server',
    GAME_STARTED:       'Connected to a running game'
}

RET_OK =        100
RET_NOK =       200
RET_RETRY =     300
RET_WAIT =      400
RET_TIMEOUT =   500

state_ret = {
    RET_OK:         'OK',
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
    (RET_OK,        SERVER_CONNECTED):      GAME_STARTED,
    (RET_NOK,       SERVER_CONNECTED):      FIND_SERVERS,
    (RET_RETRY,     SERVER_CONNECTED):      SERVER_CONNECTED,
    (RET_WAIT,      SERVER_CONNECTED):      SERVER_CONNECTED,
    (RET_TIMEOUT,   SERVER_CONNECTED):      SERVER_CONNECTED,
    (RET_OK,        GAME_STARTED):          GAME_STARTED,
    (RET_NOK,       GAME_STARTED):          FIND_SERVERS,
    (RET_RETRY,     GAME_STARTED):          GAME_STARTED,
    (RET_WAIT,      GAME_STARTED):          GAME_STARTED,
    (RET_TIMEOUT,   GAME_STARTED):          GAME_STARTED
}

