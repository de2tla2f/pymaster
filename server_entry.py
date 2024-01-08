from time import time
from struct import pack

import ipaddress

class ServerEntry:
	challenge2 = 0
	gamedir = 'valve'
	protocol = 0
	players = 0
	maxplayers = 0
	bots = 0
	gamemap = ''
	version = '0'
	servtype = 'd'
	password = 0
	os = 'l'
	secure = 0
	lan = 0
	region = 255
	product = ''
	nat = 0
	key = None

	def setInfoString(self, data):
		infostring = data.replace('\n', '').replace('\r', '').replace('\0', '')
		split = infostring.split('\\')
		for i in range(0, len(split), 2):
			try:
				value = split[i + 1]
				if( split[i] == 'challenge' ):
					self.challenge2 = int(value)
				elif( split[i] == 'gamedir' ):
					self.gamedir = value.lower() # keep gamedir lowercase
				elif( split[i] == 'protocol' ):
					self.protocol = int(value)
				elif( split[i] == 'players' ):
					self.players = int(value)
				elif( split[i] == 'max' ):
					self.maxplayers = int(value.split('.')[0])
				elif( split[i] == 'bots' ):
					self.bots = int(value)
				elif( split[i] == 'map' ):
					self.gamemap = value
				elif( split[i] == 'version' ):
					self.version = value
				elif( split[i] == 'type' ):
					self.servtype = value
				elif( split[i] == 'password' ):
					self.password = value
				elif( split[i] == 'os' ):
					self.os = value
				elif( split[i] == 'secure' ):
					self.secure = value
				elif( split[i] == 'lan' ):
					self.lan = value
				elif( split[i] == 'region' ):
					self.region = value
				elif( split[i] == 'product' ):
					self.product = value
				elif( split[i] == 'nat' ):
					self.nat = int(value)
				elif split[i] == 'key':
					self.nat = int(value, 16)
			except IndexError:
				pass
		self.check = self.challenge == self.challenge2
		return self.check

	def __init__(self, addr, challenge):
		# Address
		self.addr = addr
		# Shortcuts for generating query
		self.queryAddr = b''
		self.queryAddr += ipaddress.ip_address(addr[0]).packed
		self.queryAddr += pack('!H', int(addr[1]))

		# Random number that server must return
		self.challenge = challenge
		self.sentChallengeAt = time()

		# This server is not checked
		# So it will not get into queries
		self.check = False

		# Remove server after this time.
		# This maybe not instant
		self.die = self.sentChallengeAt + 600
