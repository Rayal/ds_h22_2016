#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 22:54:20 2016

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

# Server Class-----------------------------------------------------------------
class Server():
    def __init__(self):
        self.__serverid = server

    def listen(self, sock_addr, backlog=1):
        self.__sock_addr = sock_addr
        self.__backlog = backlog
        self.__s = socket(AF_INET, SOCK_STREAM)
        self.__s.bind(self.__sock_addr)
        self.__s.listen(self.__backlog)
        LOG.debug('Socket %s:%d is in listening state' \
                  '' % self.__s.getsockname())

    def loop(self):
        clients = []

# Main-------------------------------------------------------------------------
if __name__ == '__main__':

    server = Server()
    server.listen(('127.0.0.1',7777))
    server.loop()
    LOG.info('Terminating ...')