# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

# Imports ---------------------------------------------------------------------
import paho.mqtt.client as mqtt
import protocol.client.client_protocol as cp
import client_data.states as states
import BattleShip_UI as BUI
from protocol.common import *
from time import sleep, time
from game_logic import main
from collections import defaultdict

#def compile_servername(nickname, servername):
# Client class to initiate client object --------------------------------------
class Client():
    def __init__(self):
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
            '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)),
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

# Connect the client to server ------------------------------------------------
    def on_connect(self, client, userdata, flags, rc):
        LOG.info("Connected with result code "+str(rc))
        self.sub_to_topics()

# Client run method - find available servers, connect to server, get the game list in a server
    def run_state(self):
        #if self.waiting:
        #    if int(time()) - self.waiting_since >= self.wait_time:
        #        self.waiting = False
        #        ret = states.RET_TIMEOUT
        #    else:
        #        return
        #else:
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
        else:
            ret = states.RET_NOK

            #if ret == states.RET_WAIT:
            #    self.wait_time = 3
            #    self.waiting_since = int(time())
            #    self.waiting = True

        LOG.debug('Retcode from state %s: %s' % (states.states[self.state], states.state_ret[ret]))
        self.state = states.state_transitions[(ret, self.state)]

# Function find_servers to get a list of online servers -----------------------

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

# Response with the available server list -------------------------------------
    def found_server(self, server_name):
        try:
            self.servers.append(server_name)
            LOG.debug("Got server name: %s"%server_name)
        except NameError:
            LOG.error("Tried to append a servername to a non-existent list.")

# Function connect_to_server with the server the client wants from the list of available servers
    def connect_to_server(self):
        print("Server list: " + ', '.join(self.servers))
        if DEBUG:
            self.server = 'DEBUG_S'
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
        #self.server = ''
        #nickname = ''
        #while not self.server in self.servers:
        #    print("Server list: " + ', '.join(self.servers))
        #    self.server, nickname = raw_input('Select server to connect to and give a nickname. ').split(' ')
        #self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server, self.self)))
        #mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, server)), ' '.join((CONN_REQ, self.self, nickname)))
        #return states.RET_WAIT

# Function conn_req to get the response from the connect_to_server function ---
    def conn_req(self, response):
        if self.state != states.CONNECT_SERVER:
            return
        if response[0] == YEA:
            self.server_response[self.state] = YEA
        else:
            self.server_response[self.state] = NAY

# Function get_game_list to get the list from the connected server ---------------
    def get_game_list(self):
        self.games_list = []
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((GAME_LIST_REQ, self.self)))
        sleep(DEFAULT_WAIT_TIME)
        if self.server_response[self.state] != '':
            print('Currently open games:' + self.server_response[self.state])
        else:
            print('No games found open on the server.')

        #BUI.screen_function(self.server_response[self.state], compile_servername)

        id = '_'.join(raw_input('Select a gameID to join. Leave this space blank if you want to create your own. ').split(' '))
        #print id
        #print self.server_response[self.state]
        if id == '':
            return states.RET_RETRY

# join the existing game from the list of games available ---------------------
        if id in self.server_response[self.state]:
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((JOIN_GAME, self.self, id)))
            sleep(DEFAULT_WAIT_TIME)
            if self.server_response[self.state] == id:
                print("Connected to Game", id)
                self.gameid = id
            else:
                print("Can not connect to given gameid")
                return states.RET_NOK

# create a new game -----------------------------------------------------------
        else:
            newGameName = '_'.join(raw_input('Enter new gameName. ').split(' '))
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((CREATE_GAME, self.self, newGameName)))
            sleep(DEFAULT_WAIT_TIME)
            if self.server_response[self.state] != NAY:
                self.gameid = self.server_response[self.state]
                print('Created Game:' + self.gameid)
            else:
                print('No game created.')
                return states.RET_NOK

        self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid, self.self)))
        self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid, ACK)))

        if id in self.server_response[self.state]:
            return states.RET_OK
        return states.RET_ALT

    def send_conf(self):
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)), ' '.join((GAME_SETUP, self.self, '10 10 5 4 3 3 2')))
        sleep(DEFAULT_WAIT_TIME)
        if self.server_response[self.state] == NAY:
            return states.RET_RETRY
        return states.RET_OK

# Function game_list to get the response from the get_game_list function ------
    def game_list(self, response):
        resp = response[0]
        resp = '\n'.join(resp.split(OBJ_SEP))
        resp = ' '.join(resp.split(SUB_OBJ_SEP))
        self.server_response[self.state] = resp

# Function created_game to get the response from the create_game (new) function
    def created_game(self, response):
        self.server_response[self.state] = response

# Function joined_game to get the response from the join_game (existing) function
    def joined_game(self, response):
        self.server_response[self.state] = response[0]

    def set_ships(self):
        msg = main(self)
        mqtt_publish(self.mqtt,
                     '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
                     ' '.join((SHIP_POS, self.self, msg)))
        sleep(DEFAULT_WAIT_TIME)
        return states.RET_OK

    def start_game(self):
        #mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
        #             ' '.join((START_GAME, self.self)))
        #sleep(DEFAULT_WAIT_TIME)

        if self.server_response[self.state] == NAY:
            return states.RET_RETRY
        print self.server_response[self.state]
        return states.RET_RETRY

    def main(self):
        return states.RET_NOK

    def game_setup_reply(self, response):
        LOG.debug("Got setup reply: %s" % response)
        self.server_response[self.state] = response


    def ship_pos_reply(self, response):
        LOG.debug("Got setup reply: %s" % response)
        self.server_response[self.state] = response

    def ready_to_start_reply(self, response):
        LOG.debug("Got ready to start reply: %s" % response)
        self.server_response[self.state] = response
        if self.server_response[self.state] == READY_TO_START:
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
                         ' '.join((START_GAME, self.self)))
            self.state = states.PLAYING

    def play_turn_reply(self,response):
        LOG.debug("Play Turn reply: %s" % response)
        self.server_response[self.state] = response
        COR = raw_input('Enter coordinates. ')
        if self.server_response[self.state] == PLAY_TURN:
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, self.gameid)),
                         ' '.join((SHOOT, self.self, '0', COR)))

        sleep(DEFAULT_WAIT_TIME)
        return states.RET_OK

    def shoot_reply(self,response):
        LOG.debug("Shoot reply: %s" % response[-1])
        self.server_response[self.state] = response[-1]
        if self.server_response[self.state] == NAY:
            return states.RET_RETRY
        elif self.server_response[self.state] == SPLASH:
            print ("MISSED SHOT")
        elif self.server_response[self.state] == BOOM:
            print ("CONGRATS...YOU GOT A HIT!")


    def hit(self, response):
        print 'You have been hit by %s in: (%d:%d)'%((response[-1], int(response[0]) + 1, int(response[0]) + 1))
        #Do other stuff

    def sunk(self, response):
        if response[-1] == self.nickname:
            print 'Your ship size %s has been sunk' %response[0]
        else:
            print "%s's ship size %s has been sunk" % (response [-1], response[0])

    def lost(self, response):
        if response[-1] == self.nickname:
            print 'You lost'
        else:
            print "%s has lost" %response [-1]


    def won(self,response):
        if response[-1] == self.nickname:
            print 'You won'
        else:
            print "%s has lost" %response [-1]

    def game_over(self,response):
        if response[-1] == GAME_OVER:
            print 'Game over'

client = Client()
try:
    client.run()
except KeyboardInterrupt:
    client.stop()
