# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

import paho.mqtt.client as mqtt
import protocol.client.client_protocol as cp
import client_data.states as states

from protocol.common import *
from time import sleep, time


SELF += 'C'

class Client():
    def __init__(self):
        self.topics = []
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, SELF)))
        self.nickname = SELF + 'Cn'

        self.client = mqtt.Client()
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc)
        self.client.on_message = lambda client, userdata, msg: cp.message_in(self, client, userdata, msg)

        self.client.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)
        self.waiting = False
        self.wait_time = 0
        self.waiting_since = 0

    def start_blocking(self):
        self.client.loop_forever()

    def start_nonblocking(self):
        self.client.loop_start()

    def run(self):
        self.start_nonblocking()
        self.state = states.FIND_SERVERS
        while True:
            self.run_state()
            sleep(3)

    def add_topic(self, topic):
        self.topics.append(topic)
        self.client.subscribe(topic)

    def remove_topic(self, topic):
        self.topics.remove(topic)
        self.client.unsubscribe(topic)

    def sub_to_topics(self):
        for topic in self.topics:
            LOG.info("Subscribing to: %s" % topic)
            self.client.subscribe(topic)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        LOG.info("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.sub_to_topics()

    def run_state(self):
        if self.waiting:
            if int(time()) - self.waiting_since >= self.wait_time:
                self.waiting = False
                ret = states.RET_TIMEOUT
            else:
                return
        else:
            if self.state == states.FIND_SERVERS:
                ret = self.find_servers()
            elif self.state == states.CONNECT_SERVER:
                ret = self.connect_to_server()
            else:
                ret = states.RET_NOK

            if ret == states.RET_WAIT:
                self.wait_time = 3
                self.waiting_since = int(time())
                self.waiting = True

        LOG.debug('Retcode from state %s: %s' % (states.states[self.state], states.state_ret[ret]))
        self.state = states.state_transitions[(ret, self.state)]

    def find_servers(self):
        LOG.debug("Finding online servers")
        self.servers = []
        mqtt_publish(self.client, '/'.join((DEFAULT_ROOT_TOPIC, GLOBAL)), ' '.join((SOUND_OFF, SELF)))
        sleep(3)
        if len(self.servers):
            return states.RET_OK
        else:
            return states.RET_RETRY

    def found_server(self, server_name):
        try:
            self.servers.append(server_name)
            LOG.debug("Got server name: %s"%server_name)
        except NameError:
            LOG.error("Tried to append a servername to a non-existent list.")

    def connect_to_server(self):
        server = ''
        nickname = ''
        while not server in self.servers:
            print("Server list: " + ', '.join(self.servers))
            server, nickname = raw_input('Select server to connect to and give a nickname. ').split(' ')
        self.add_topic('/'.join((DEFAULT_ROOT_TOPIC, SERVER, server, SELF)))
        mqtt_publish(self.client, '/'.join((DEFAULT_ROOT_TOPIC, SERVER, server)), ' '.join((CONN_REQ, SELF, nickname)))
        return states.RET_WAIT

    def conn_req(self, response):
        if (not self.waiting) or (self.state != states.CONNECT_SERVER):
            return
        if response[0] == YEA:
            self.state = states.SERVER_CONNECTED
        else:
            self.state = states.FIND_SERVERS
        self.waiting == False


client = Client()
client.run()
