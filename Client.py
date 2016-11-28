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


# Client Class-----------------------------------------------------------------
class Client():

    def __init__(self):
        self.__on_recv = None
        self.__on_published = None

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

    if c.connect(('127.0.0.1',7777)):

        t = Thread()
        t.start()

        c.loop()
        t.join()

    logging.info('Terminating')