#!/usr/bin/env python3
# Basic networking
import socket

# Challenge generator
import random

# System important... things
import sys
import traceback
import logging

# Network packet creating
from struct import pack

# Server time control
from time import time

# ServerEntry class module
from server_entry import ServerEntry
# Protocol class
from protocol import MasterProtocol

UDP_IP = "0.0.0.0"
UDP_PORT = 27010
LOG_FILENAME = 'pymaster.log'
logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().addHandler(logging.FileHandler(LOG_FILENAME))
logging.getLogger().setLevel(logging.DEBUG)

def logPrint( msg ):
	logging.debug( msg )

class PyMaster:
	serverList = []
	sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
	
	def __init__(self):
		self.sock.bind( (UDP_IP, UDP_PORT) )

		logPrint("Welcome to PyMaster!")
		logPrint("I ask you again, are you my master?")
		logPrint("Running on {0}:{1}".format( UDP_IP, UDP_PORT))
	
	def serverLoop(self):
		data, addr = self.sock.recvfrom(1024)
		data = data.decode('latin_1')
		
		if( data[0] == MasterProtocol.clientQuery ):
			self.clientQuery(data, addr)
		elif( data[0] == MasterProtocol.challengeRequest ):
			self.sendChallengeToServer(data, addr)
		elif( data[0] == MasterProtocol.addServer ):
			self.addServerToList(data, addr)
		elif( data[0] == MasterProtocol.removeServer ):
			self.removeServerFromList(data, addr)
		elif( data[0] == MasterProtocol.statusRequest ):
			self.sendStatus(data, addr)
		else:
			logPrint("Unknown message: {0} from {1}:{2}".format(data, addr[0], addr[1]))

	def clientQuery(self, data, addr):
		logPrint("Client Query: from {0}:{1}".format(addr[0], addr[1]))
		
		region = data[1] # UNUSED
		data = data.strip('1' + region)
		try:
			query = data.split('\0')
		except ValueError:
			logPrint(traceback.format_exc())
			return
		
		queryAddr = query[0] # UNUSED
		rawFilter = query[1]
		
		# Remove first \ character
		rawFilter = rawFilter.strip('\\')
		split = rawFilter.split('\\')
		
		# Use NoneType as undefined
		gamedir   = None
		gamemap   = None # UNUSED: until Xash3D will not support full filter
		
		for i in range( 0, len(split), 2 ):
			try:
				key = split[i + 1]
				if( split[i] == 'gamedir' ):
					gamedir = key
				elif( split[i] == 'map' ):
					gamemap = key
				else:
					logPrint('Unhandled info string entry: {0}/{1}'.format(split[i], key))
			except IndexError:
				pass

		packet = MasterProtocol.queryPacketHeader
		for i in self.serverList:
			if(  time() > i.die ):
				self.serverList.remove(i)
				continue
			
			if( not i.check ):
				continue
			
			if( gamedir != None ):
				if( gamedir != i.gamedir):
					continue
			
			# Use pregenerated address string
			packet += i.queryAddr
			logPrint('Append server to answer: {0}:{1}'.format(i.addr[0], i.addr[1]))
			
		self.sock.sendto(packet, addr)
	
	def removeServerFromList(self, data, addr):
		logPrint("Remove Server: from {0}:{1}".format(addr[0], addr[1]))
		for i in self.serverList:
			if (i.addr == addr):
				self.serverList.remove(i)
	
	def sendChallengeToServer(self, data, addr):
		logPrint("Challenge Request: from {0}:{1}".format(addr[0], addr[1]))
		# At first, remove old server- data from list
		self.removeServerFromList(None, addr)
		
		# Generate a 32 bit challenge number
		challenge = random.randint(0, 2**32-1)
		
		# Add server to list
		self.serverList.append(ServerEntry(addr, challenge))
		
		# And send him a challenge
		packet = MasterProtocol.challengePacketHeader
		packet += pack('I', challenge)
		self.sock.sendto(packet, addr)

	def addServerToList(self, data, addr):
		logPrint("Add Server: from {0}:{1}".format(addr[0], addr[1]))
		# Remove the header. Just for better parsing.
		serverInfo = data.strip('\x30\x0a\x5c')
		
		# Find a server with same address
		for serverEntry in self.serverList:
			if( serverEntry.addr == addr ):
				break
			
		serverEntry.setInfoString( serverInfo )
	
	def sendStatus( self, data, addr ):
		logPrint("Status Request: from {0}:{1}".format(addr[0], addr[1]))
		count = len(self.serverList)
		
		packet = b'Server\t\t\tGame\tMap\tPlayers\tVersion\tChallenge\tCheck\n'
		for i in self.serverList:
			line = '{0}:{1}\t{2}\t{3}\t{4}/{5}\t{6}\n'.format(i.addr[0], i.addr[1], 
													 i.gamedir, i.gamemap, i.players, 
													 i.maxplayers, i.version, i.challenge, i.check)
			packet += line.encode('latin_1')
		self.sock.sendto(packet, addr)


def main( argv = None ):
	if argv is None:
		argv = sys.argv
	
	masterMain = PyMaster()
	while True: 
		try:
			masterMain.serverLoop()
		except Exception:
			logPrint(traceback.format_exc())
			pass

if __name__ == "__main__":
	sys.exit( main( ) )