import paho.mqtt.client as mqtt
from sys import argv
from protocol.common import *
from time import sleep

if DEBUG:
	SELF = "TEST"

topics = []
topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, SELF)))
client = mqtt.Client()

def unsub_from_topic(client, topic):
	print ("Unsubscribing from %s"%topic)
	client.unsubscribe(topic)
	global topics
	topics.remove(topic)

def sub_to_topics(client):
	global topics
	for topic in topics:
		print("Subscribing to: %s" % topic)
		client.subscribe(topic)

def on_connect(client, userdata, flags, rc):
	sub_to_topics(client)

def on_message(client, userdata, msg):
	print("Got message: %s %s"%(msg.topic, msg.payload))
	state_machine(client, msg)


client.on_connect = on_connect
client.on_message = on_message
client.connect(DEFAULT_SERVER_URL)
client.loop_start()

INIT = 1
SERVERS_FOUND = 2
SERVER_CONNECTED = 3
SETUP_GAME = 4

state = INIT

def state_machine(client, msg = None):
	global state
	global INIT
	global SERVERS_FOUND
	global SERVER_CONNECTED
	global FIND_GAME
	global SETUP_GAME

	print("STATE: %d"%state)

	if state == INIT:
		if init(client, msg):
			state += 1
		msg = None

	if state == SERVERS_FOUND:
		res = servers_found(client, msg)
		if res == 1:
			state += 1
		elif res == -1:
			state -= 1
		msg = None

	if state == SERVER_CONNECTED:
		if server_connected(client, msg):
			state += 1
		msg = None

	if state == SETUP_GAME:
		if setup_game(client, msg):
			state += 1
		msg = None

server = ""

def init(client, msg):
	if msg == None:
		mqtt_publish(client, "/".join((DEFAULT_ROOT_TOPIC, GLOBAL)), " ".join((SOUND_OFF, SELF)))

	elif "posix" in msg.payload or "DEBUG_SERVER" in msg.payload:
		global server
		server = msg.payload.split(" ")[-1]
		return True

def servers_found(client, msg):
	global server
	if msg == None:
		mqtt_publish(client, "/".join((DEFAULT_ROOT_TOPIC, SERVER, server)),
		" ".join((CONN_REQ, SELF, SELF+"derp")))
		topics.append("/".join((DEFAULT_ROOT_TOPIC, SERVER, server, SELF)))
		sub_to_topics(client)
		return 0
	if YEA in msg.payload:
		return 1
	if NAY in msg.payload:
		unsub_from_topic(client, "/".join((DEFAULT_ROOT_TOPIC, SERVER, server, SELF)))
		server = ""
		return -1

game_id = ""
def server_connected(client, msg):
	if argv[-1] == "join" and msg == None:
		mqtt_publish(client, "/".join((DEFAULT_ROOT_TOPIC, SERVER, server)),
		" ".join((GAME_LIST_REQ, SELF)))
	elif msg == None:
		mqtt_publish(client, "/".join((DEFAULT_ROOT_TOPIC, SERVER, server)),
		" ".join((CREATE_GAME, SELF, "GAMENAME")))
	elif argv[-1] == "join" and SUB_OBJ_SEP in msg.payload:
		game_id = msg.payload.split(SUB_OBJ_SEP)[0]
		mqtt_publish(client, "/".join((DEFAULT_ROOT_TOPIC, SERVER, server)),
		" ".join((JOIN_GAME, SELF, game_id)))
	elif not NAY in msg.payload:
		global game_id
		game_id = msg.payload
		topics.append("/".join((DEFAULT_ROOT_TOPIC, GAME, server, game_id)))
		sub_to_topics(client)
		if argv[-1] != "join":
			mqtt_publish(client, "/".join((DEFAULT_ROOT_TOPIC, GAME, server, game_id)),
			" ".join((GAME_SETUP, SELF, "5 5 5 5 5")))
		return True

	return False
	pass

def setup_game(client, msg):
	mqtt_publish(client, "/".join((DEFAULT_ROOT_TOPIC, GAME, server, game_id)),
	" ".join((SHIP_POS, SELF, OBJ_SEP.join([
	SUB_OBJ_SEP.join(["5", "0", "0", "0"]),
	SUB_OBJ_SEP.join(["5", "0", "1", "0"]),
	SUB_OBJ_SEP.join(["5", "0", "2", "0"]),
	]))))
	return True

while True:
	state_machine(client)
	sleep(3)
