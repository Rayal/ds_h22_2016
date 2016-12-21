# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.CRITICAL,format=FORMAT)
LOG = logging.getLogger()

# Imports ---------------------------------------------------------------------
import paho.mqtt.client as mqtt
import protocol.client.client_protocol as cp
import client_data.states as states
import BattleShip_UI as BUI
import numpy as np
from protocol.common import *
from time import sleep, time
from game_logic import main
from collections import defaultdict
from sys import argv
from attack_client import main_attack

# Client class to instantiate client object -----------------------------------
class Client():
    def __init__(self):
        if len(argv) > 1:
            self.self = argv[-1]
        else:
            self.self = SELF + 'C'
        self.topics = []
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, self.self)))

        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc)
        self.mqtt.on_message = lambda client, userdata, msg: cp.message_in(self, client, userdata, msg)

        self.mqtt.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)

        self.waiting = False
        self.wait_time = 0
        self.waiting_since = 0
        self.server_response = defaultdict(lambda: NAY)
        self.creator = False

# Start Client loop -----------------------------------------------------------

        self.nickname = ''

    def start_blocking(self):
        self.mqtt.loop_forever()

    def start_nonblocking(self):
        self.mqtt.loop_start()

# Client run ------------------------------------------------------------------
    def run(self):
        self.start_nonblocking()
        self.state = states.FIND_SERVERS
        while True:
            self.run_state()
            sleep(DEFAULT_WAIT_TIME)

    def stop(self):
        try:
            mqtt_publish(self.mqtt,
                '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
                ' '.join((EXIT, self.self)))
        except AttributeError:
            pass

        mqtt_publish(self.mqtt,
            '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.self)),
            ' '.join((DISCONNECT, self.self)))

        self.mqtt.disconnect()

# mqtt topics - add, remove, subscribe and unscribe ---------------------------
    def add_topic(self, topic):
        self.topics.append(topic)
        self.mqtt.subscribe(topic)

    def remove_topic(self, topic):
        self.topics.remove(topic)
        self.mqtt.unsubscribe(topic)

    def sub_to_topics(self):
        for topic in self.topics:
            LOG.info("Subscribing to: %s" % topic)
            self.mqtt.subscribe(topic)

    '''Connect the client to server ------------------------------------------------
    @params : client, userdata, flags
    calls function: sub_to topics  to subscribe
    '''

    def on_connect(self, client, userdata, flags, rc):
        LOG.info("Connected with result code "+str(rc))
        self.sub_to_topics()

    ''' Client run method - find available servers, connect to server, get the game list in a server
    It works like a state machine
    And defines what state should be followed next
    '''
    def run_state(self):

        if self.state == states.FIND_SERVERS:
            ret = self.find_servers()
        elif self.state == states.CONNECT_SERVER:
            ret = self.connect_to_server()
        elif self.state == states.SERVER_CONNECTED:
            ret = self.get_game_list()
        elif self.state == states.GAME_CONFIG:
            ret = self.send_conf()
        elif self.state == states.SET_SHIPS:
            ret = self.set_ships()
        elif self.state == states.GAME_STARTED:
            ret = self.main()
        elif self.state == states.PLAYING:
            ret = self.main()
        else:
            ret = states.RET_NOK


        LOG.debug('Retcode from state %s: %s' % (states.states[self.state], states.state_ret[ret]))
        self.state = states.state_transitions[(ret, self.state)]

    '''Function find_servers to get a list of online servers -----------------------
    @params : self
    Outputs : finds a list of online available servers using the SOUND_OFF function
    '''

    def find_servers(self):
        LOG.debug("Finding online servers")
        self.servers = []
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GLOBAL)), ' '.join((SOUND_OFF, self.self)))
        sleep(DEFAULT_WAIT_TIME)
        if len(self.servers):
            return states.RET_OK
        else:
            # TODO: Timeout, to give up
            return states.RET_RETRY

    '''Response with the available server list -------------------------------------
    @params: A response containing the names of available servers
    Output : Prints the list of available servers
    '''
    def found_server(self, server_name):
        try:
            self.servers.append(server_name)
            LOG.debug("Got server name: %s"%server_name)
        except NameError:
            LOG.error("Tried to append a servername to a non-existent list.")

    '''Function connect_to_server to connect with the server the client wants from the list of available servers
    Function conn_req from the client_functions.py is used
    @params : self
    Output :  Connection request successful or again a retry
    '''
    def connect_to_server(self):
        print("Server list: " + ', '.join(self.servers))
        if DEBUG:
            self.server = 'DEBUG_S'
            if len(argv) > 1:
                self.nickname = argv[-1] + 'name'
            else:
                self.nickname = 'DEBUG_NAME'
        else:
            try:
                self.server, self.nickname = raw_input('Select server to connect to and give a nickname. ').split(' ')
            except ValueError:
                return states.RET_NOK
        if not self.server in self.servers:
            return states.RET_NOK
        self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server, self.self)))
        self.server_response[self.state] = NAY
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((CONN_REQ, self.self, self.nickname)))
        sleep(DEFAULT_WAIT_TIME)
        if self.server_response[self.state] == YEA:
            return states.RET_OK
        return states.RET_NOK


    '''Function conn_req to get the response from the connect_to_server function ---
    @params: A response from the conn_req function of client_functions.py
    Output : Connection successful or not
    '''
    def conn_req(self, response):
        if self.state != states.CONNECT_SERVER:
            return
        if response[0] == YEA:
            self.server_response[self.state] = YEA
        else:
            self.server_response[self.state] = NAY

    '''Function get_game_list to get the list from the connected server ---------------
    @params: self
    Output : The open games list in the format - GAMEID GAMENAME NICKNAME separated by a separator
    '''
    def get_game_list(self):
        self.games_list = []
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((GAME_LIST_REQ, self.self)))
        sleep(DEFAULT_WAIT_TIME)
        if self.server_response[self.state] != '':
            print('Currently open games:' + self.server_response[self.state])
        else:
            print('No games found open on the server.')


        id = '_'.join(raw_input('Select a gameID to join. Leave this space blank if you want to create your own. ').split(' '))
        print id
        if id == '':
            return states.RET_RETRY

        '''JOIN THE EXISTING GAME from the list of games available ---------------------
        From the list of available games, the user inputs the id of the game he wants to join in
        '''
        game_ids = [g.split(' ')[0] for g in self.server_response[self.state].split('\n')]
        if id in game_ids:
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((JOIN_GAME, self.self, id)))
            sleep(DEFAULT_WAIT_TIME)
            if self.server_response[self.state] == id:
                print("Connected to Game", id)
                self.gameid = id
            else:
                print("Can not connect to given gameid")
                return states.RET_NOK

            '''CREATE A NEW GAME ----------------------------------------------
            From the list of available games, if the user does not want to join any game,
            he should create one by giving a new gamename
            '''

        else:
            newGameName = '_'.join(
                raw_input('Enter new gameName. ').split(' '))
            mqtt_publish(
                self.mqtt,
                '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)),
                ' '.join((CREATE_GAME, self.self, newGameName)))
            sleep(DEFAULT_WAIT_TIME)
            if self.server_response[self.state] != NAY:
                self.gameid = self.server_response[self.state]
                print('Created Game: ' + self.gameid)
                self.creator = True
            else:
                print('No game created.')
                return states.RET_NOK

        self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid, self.self)))
        self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid, ACK)))

        if id in self.server_response[self.state]:
            return states.RET_OK
        return states.RET_ALT

    '''Function to send the configuration of the game - the board dimensions and the ship sizes
    @params: self
    Output : Returns states OK or Retry
    '''
    def send_conf(self):
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)), ' '.join((GAME_SETUP, self.self, '10 10 5 4 3 3 2')))
        sleep(DEFAULT_WAIT_TIME)
        if self.server_response[self.state] == NAY:
            return states.RET_RETRY
        return states.RET_OK

    '''Function game_list to get the response from the get_game_list function ------
    @params: A response from the game_list_req function from the client_functions.py file
    Output : the game list
    '''
    def game_list(self, response):
        resp = response[0]
        resp = '\n'.join(resp.split(OBJ_SEP))
        resp = ' '.join(resp.split(SUB_OBJ_SEP))
        self.server_response[self.state] = resp

    '''Function created_game to get the response from the create_game (new) function
    @params: A response from the create_game function from the client_functions.py file
    Output : the created game
    '''
    def created_game(self, response):
        self.server_response[self.state] = response

    '''Function joined_game to get the response from the join_game (existing) function
    '''
    def joined_game(self, response):
        self.server_response[self.state] = response[0]

    '''Function set_ships to set the ships at some coordinates
    '''
    def set_ships(self):
        msg = main(self)
        mqtt_publish(self.mqtt,
                     '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
                     ' '.join((SHIP_POS, self.self, msg)))
        sleep(DEFAULT_WAIT_TIME)
        return states.RET_OK

    '''Function start_game to start the game
    @params: self
    Output: Retry or Ok state
    '''
    def start_game(self):

        if self.server_response[self.state] == NAY:
            return states.RET_RETRY
        print self.server_response[self.state]
        return states.RET_RETRY

    '''Function to use the UI and call the functions of the game logic'''
    def main(self):
        return states.RET_RETRY

    '''Function game_Setup_reply to get the response from the game_setup function
        @params: A response from the game_setup  function from the game_functions.py file as a "YEA" or "NAY"
    '''
    def game_setup_reply(self, response):
        LOG.debug("Got setup reply: %s" % response)
        self.server_response[self.state] = response

    '''Function ship_pos_reply to get the response from the ship_pos function
        @params: A response from the ship_pos function from the game_functions.py file as a "YEA" or "NAY"
    '''

    def ship_pos_reply(self, response):
        LOG.debug("Got setup reply: %s" % response)
        self.server_response[self.state] = response

    '''Function ready_to_start_reply to get the response from the ready_to_start function
            @params: A response from the ready_to_start function from the game_functions.py file as a "READY_TO_START"
            Output : PLAYING state
        '''

    def start_game(self):
        self.state = states.PLAYING

    def ready_to_start_reply(self):
        if self.creator:
            LOG.debug("Got ready to start.")
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
                             ' '.join((START_GAME, self.self)))

    '''Function play_turn_reply to get the response from the play_turn function
        @params: A response from the play_turn function from the game_functions.py file as a "PLAY_TURN"
         '''

    def play_turn_reply(self):
        if self.state != states.PLAYING:
            return
        LOG.debug("Play Turn received")
        while True:
            self.coor = raw_input('Enter the X and Y coordinates in the format X Y ')
            self.coor = np.array(self.coor.split(' ')).astype(int)
            if not((self.coor < [1, 1]).all() or (self.coor > [10, 10]).all()):
                break
            print('Coordinates out of boundaries. Try again.')

        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
                     ' '.join((SHOOT, self.self, '0', str(self.coor).strip('[]'))))

    '''Function shoot_reply to get the response from the shoot function
        @params: A response from the shoot function from the game_functions.py file as a NAY, SPLASH or BOOM
        '''
    def shoot_reply(self,response):
        LOG.debug("Shoot reply: %s" % response[-1])
        if response[-1] == NAY:
            return states.RET_RETRY
        elif response[-1] == SPLASH:
            print ("MISSED SHOT")
            main_attack(self.coor, "miss")
        elif response[-1] == BOOM:
            print ("YAY...YOU GOT A HIT!")
            main_attack(self.coor, "hit")

    '''Function hit to get response from the function hit in the game_functions.py file as a HIT or NOt
    '''
    def hit(self, response):
        print response
        print 'You have been hit by %s in: (%d,%d)'%((response[-1], int(response[0]) + 1, int(response[1]) + 1))
        #Do other stuff

    '''Function sunk to get response from the function sunk in the game_functions.py file if the ships sunk or not
        '''
    def sunk(self, response):
        if response[-1] == self.nickname:
            print 'Your ship size %s has been sunk' %response[0]
        else:
            print "%s's ship size %s has been sunk" % (response [-1], response[0])

    '''Function lost to get response from the function lost in the game_functions.py file if the ships sunk and who lost
            '''
    def lost(self, response):
        if response == self.nickname:
            print 'You lost'
        else:
            print "%s has lost" %response

    '''Function won to get response from the function won in the game_functions.py file if the ships sunk and who won
                '''
    def won(self,response):
        if response == self.nickname:
            print 'You won'
        else:
            print "%s has won" %response

        self.close()

    '''Function game_over to get response from the function game_over in the game_functions.py file if the game is over
                '''
    def game_over(self):
        print 'Game over'
        self.stop()

client = Client()
try:
    client.run()
except KeyboardInterrupt:
    client.stop()
