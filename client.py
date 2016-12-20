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


# Client extension ------------------------------------------------------------

SELF += 'C'

#def compile_servername(nickname, servername):
# Client class to initiate client object --------------------------------------
class Client():
    def __init__(self):
        self.topics = []
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, SELF)))

        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc)
        self.mqtt.on_message = lambda client, userdata, msg: cp.message_in(self, client, userdata, msg)

        self.mqtt.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)

        self.waiting = False
        self.wait_time = 0
        self.waiting_since = 0
        self.server_response = {}

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
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, GLOBAL)), ' '.join((SOUND_OFF, SELF)))
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
            self.server, self.nickname = raw_input('Select server to connect to and give a nickname. ').split(' ')
        if not self.server in self.servers:
            return states.RET_NOK
        self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server, SELF)))
        self.server_response[self.state] = NAY
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((CONN_REQ, SELF, self.nickname)))
        sleep(DEFAULT_WAIT_TIME)
        if self.server_response[self.state] == YEA:
            return states.RET_OK
        return states.RET_NOK
        #self.server = ''
        #nickname = ''
        #while not self.server in self.servers:
        #    print("Server list: " + ', '.join(self.servers))
        #    self.server, nickname = raw_input('Select server to connect to and give a nickname. ').split(' ')
        #self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server, SELF)))
        #mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, server)), ' '.join((CONN_REQ, SELF, nickname)))
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
        mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((GAME_LIST_REQ, SELF)))
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
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((JOIN_GAME, SELF, id)))
            sleep(DEFAULT_WAIT_TIME)
            if self.server_response[self.state] == id:
                print("Connected to Game", id)
            else:
                print("Can not connect to given gameid")

# create a new game -----------------------------------------------------------
        else:
            newGameName = '_'.join(raw_input('Enter new gameName. ').split(' '))
            mqtt_publish(self.mqtt, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, self.server)), ' '.join((CREATE_GAME, SELF, newGameName)))
            sleep(DEFAULT_WAIT_TIME)
            if self.server_response[self.state] != '':
                newgameIDcreated = self.server_response[self.state]
                print('Created Game:' + self.server_response[self.state])
            else:
                print('No game created.')
            newgameIDcreated = self.server_response[self.state]
            #print newgameIDcreated
            #newgame = [newgameIDcreated, newGameName]
            self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, GAME, self.server, newgameIDcreated, ACK)))

        return states.RET_OK

# Function game_list to get the response from the get_game_list function ------
    def game_list(self, response):
        self.server_response[self.state] = response[0]

# Function created_game to get the response from the create_game (new) function
    def created_game(self, response):
        self.server_response[self.state] = response[0]

# Function joined_game to get the response from the join_game (existing) function
    def joined_game(self, response):
        self.server_response[self.state] = response[0]

    def main(self):
        main(self)
        return states.RET_OK

client = Client()
client.run()


