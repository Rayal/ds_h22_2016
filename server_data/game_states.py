INIT =              1
WAITING_TO_START =  2
PLAY =              2
POST_PLAY =         3

RET_OK =        100
RET_NOK =       200
RET_RETRY =     300
RET_WAIT =      400
RET_TIMEOUT =   500

state_transitions = {
    (INIT, RET_OK):     PLAY,
    (INIT, RET_NOK):    POST_PLAY
}

DEFAULT_TURN_SPEED = 180
