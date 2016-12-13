FIND_SERVERS =      1
CONNECT_SERVER =    2

states = {
    FIND_SERVERS:   'Find Servers',
    CONNECT_SERVER: 'Connect to Server'
}

RET_OK =        100
RET_NOK =       200
RET_RETRY =     300

state_ret = {
    RET_OK:         'OK',
    RET_NOK:        'NOK',
    RET_RETRY:      'Retry'
}

state_transitions = {
    (RET_OK, FIND_SERVERS):         CONNECT_SERVER,
    (RET_NOK, FIND_SERVERS):        FIND_SERVERS,
    (RET_RETRY, FIND_SERVERS):      FIND_SERVERS,
    (RET_OK, CONNECT_SERVER):       CONNECT_SERVER,
    (RET_NOK, CONNECT_SERVER):      CONNECT_SERVER,
    (RET_RETRY, CONNECT_SERVER):    CONNECT_SERVER
}
# class State():
#     def __init__(self, function, next_state = None, prev_state = None):
#         self.function = function
#         if next_state:
#             self.next_state = next_state
#         if prev_state:
#             self.prev_state = prev_state
#
#     def run(self):
#         retval = function()
#         if retval == RET_OK:
#             try:
#                 return self.next_state
#             except NameError:
#                 return (None, RET_OK)
#         elif retval == RET_FAIL:
#             try:
#                 return self.prev_state
#             except NameError:
#                 return (None, RET_FAIL)
#         else:
#             return self
#
#     def set_prev(self, state):
#         self.prev_state = state
#
#     def set_next(self, state):
#         self.next_state = state
