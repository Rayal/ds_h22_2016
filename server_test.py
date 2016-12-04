import paho.mqtt.publish as publish
from sys import argv

server = argv[-1]
msgs = [("DS2016_BATTLESHIP/S/posix%s"%server,"13 YOU GAME", 0, False),\
	("DS2016_BATTLESHIP/S/posix%s"%server,"14 ME GAME", 0, False),\
	("DS2016_BATTLESHIP/S/posix%s"%server,"10 ME NICK", 0, False),\
	("DS2016_BATTLESHIP/S/posix%s"%server,"10 YOU NAME", 0, False)
	]
publish.multiple(msgs, hostname="iot.eclipse.org")
