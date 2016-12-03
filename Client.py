#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 22:56:20 2016

@author: Andreas Ragen Ayal
@author: Rezwan Islam
@author: Samreen Mahak Hassan
"""
# Setup Python logging ------------------ -------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

# Imports----------------------------------------------------------------------
from threading import Thread, Lock
from time import time
from socket import AF_INET, SOCK_STREAM, socket
from time import asctime,localtime
import paho.mqtt.client as mqtt
import protocol.client.client_protocol as cp
import protocol.client.client_functions as cf
from protocol.common import *
from server_data.game_obj import Game
import random as rnd

# Client Class-----------------------------------------------------------------
class Client():

    def __init__(self, nickname, client, clientID):
        self.name = name
        self.nickname = nickname
        self.clientID = clientID
        self.client = mqtt.Client()
        self.nickname = nickname

        self.__on_recv = None
        self.__on_published = None

        self.client = mqtt.Client()
        self.client.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)
        self.client.mqtt.loop.start()

        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc)
        self.client.on_message = lambda client, userdata, msg: cp.message_in(self, client, userdata, msg)

        def on_connect(self, client, userdata, flags, rc):
            LOG.info("Connected with result code " + str(rc))


        #soundoff
        client.conn_req(self, mqtt, clientID, nickname)




        self.client.mqtt.loop.stop()


# Main-------------------------------------------------------------------------

if __name__ == '__main__':
    def on_recv(msg):
        if len(msg) > 0:
            msg = msg.split(' ')
            msg = tuple(msg[:3]+[' '.join(msg[3:])])
            t_form = lambda x: asctime(localtime(float(x)))
            m_form = lambda x: '%s [%s:%s] -> '\
                        '%s' % (t_form(x[0]),x[1],x[2],x[3].decode('utf-8'))
            m = m_form(msg)
            logging.info('\n%s' % m)

    def on_publish():
        logging.info('\n Message published')

    c = Client()
    c.set_on_published_callback(on_publish)
    c.set_on_recv_callback(on_recv)

   # if c.connect(('127.0.0.1',7777)):

        t = Thread()
        t.start()

        c.loop()
        t.join()

    logging.info('Terminating')