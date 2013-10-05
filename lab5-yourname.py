## Netwerken en Systeembeveiliging Lab 5 - Distributed Sensor Network
## NAME:
## STUDENT ID:
"""
DONE
 - The mcastSocket is only a listener
 - All messages are send with the peerSocket
 - Ping Pong Neighbour works
 - List works
 - Ping interval
TODO
 - Check if position is already taken
BUGS
 - 
"""
import sys
import struct
import select
from socket import *
from random import randint
from gui import MainWindow
from sensor import *
import time


# Get random position in NxN grid.
def random_position(n):
	x = randint(0, n)
	y = randint(0, n)
	return (x, y)

class msgParser:
	__node = None
	def __init__(self, node):
		self.__node = node
	def parseLine(self, line):
		if line == "ping":
			self.__node.ping()
		elif line == "list":
			self.__node.listNeighbours()
		elif line == "move":
			self.__node.moveNode()
		else:
			self.__node.log("No command for %s" % line)
	def parseConnection(self, conn):
		raw, addr = conn.recvfrom(1024)
		self.parseSensorMessage(raw, addr)
	def parseSensorMessage(self, msg, addr):
		mType, seq, initor, neighbour, op, data = message_decode(msg)
		if mType == MSG_PING:
			self.__node.pong(initor, addr)
		elif mType == MSG_PONG:
			self.__node.addNeighbour(neighbour, addr)
		else:
			self.__node.log("Received %d from %s:%s on (%d,%d), unknown mType" \
				% (mType, addr[0], addr[1], neighbour[0], neighbour[1]))
		

class neighbours:
	__node = None
	__dict = {}
	def __init__(self, node):
		self.__node = node
	def add(self, pos, addr):
		self.__dict[pos] = addr
	def clear(self):
		self.__dict.clear()
	def __str__(self):
		import operator
		retr = "(x,y)\t\taddress:port\n"
		for key in self.__dict:
			diff = tuple(map(operator.div, key, self.__node.position))
			self.__node.log("pos: (%d,%d)\n" % (self.__node.position[0], self.__node.position[1]))
			#self.__node.log("pos: (%d,%d)" % diff[0], diff[1])
			node = self.__dict[key]
			distance = self.__node.distanceTo(diff)
			retr += "(%d,%d):\t\t%s:%s dist: %d\n" % (key[0], key[1], node[0], node[1], distance)
		return retr
		

class nodeContainer:
	"""
	Node wrapper
	"""
	__neighbours = None
	__window = None
	
	__host = ''
	__mcastAddr = None
	address = None
	peerSocket = None
	mcastSocket = None

	position = None
	value = None
	range = 50
	pingTime = 30 
	__lastPing = 0
	__debug = 1

	def __init__(self):
		# Multicast listener socket
		self.mcastSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.mcastSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

		# Peer socket
		self.peerSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.peerSocket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 5)
		
		self.__host = ''
		self.__neighbours = neighbours(self)
	""" Initiate sockets """
	def init(self, mcast_addr):
		self.__mcastAddr = mcast_addr
		self.mcastSocket.bind( (self.__host, mcast_addr[1]) )
		self.peerSocket.bind( (self.__host, INADDR_ANY) )

		self.address = self.peerSocket.getsockname()

		# Subscribe the socket to multicast messages from the given address.
		mreq = struct.pack('=4sl', inet_aton(mcast_addr[0]), INADDR_ANY)
		self.mcastSocket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
	def getConnections(self):
		return [self.mcastSocket, self.peerSocket]
	""" Window operations """
	def createWindow(self):
		window = MainWindow()
		window.writeln( 'my address is %s:%s' % self.address )
		window.writeln( 'my position is (%s, %s)' % self.position )
		window.writeln( 'my sensor value is %s' % self.value )
		self.__window = window
		return window
	def log(self, msg, level=0):
		if self.__debug > level:
			timeStr = time.strftime("%H:%M:%S")
			self.__window.writeln("[%s]: %s" % (timeStr, msg))
	""" Neighbour operations """
	def addNeighbour(self, pos, addr):
		self.log("Recieved PONG from %s:%s at (%d,%d) " \
			% (addr[0], addr[1], pos[0], pos[1]), 1)
		if self.inRange(pos):
			self.__neighbours.add(pos, addr)
			self.log("Found neighbour (%d,%d)" % pos)
	def listNeighbours(self):
		self.log("/-- Current known neighbours --\\")
		self.log(str(self.__neighbours))
		self.log("\\-- Current known neighbours --/")
	def inRange(self, pos):
		import operator
		diff = tuple(map(operator.div, pos, self.position))
		distance = self.distanceTo(diff)
		self.log("pos (%d,%d)" % (pos[0], pos[1]))
		self.log("self (%d,%d)" % (self.position[0], self.position[1]))
		self.log("diff (%d,%d)" % (diff[0], diff[1]))
		self.log("distance (%d)" % distance)
		return distance < self.range
	def distanceTo(self, diff):
		import math
		distance = math.sqrt(diff[0] ** 2 + diff[1] ** 2)
		return distance
	""" Protocol operations """
	def autoPing(self):
		if self.pingTime < 1:
			return
		if self.__lastPing + self.pingTime < time.time():
			self.ping()
			self.__lastPing = time.time()
	def ping(self):
		self.log("Cleared neighbour list", 1)
		self.__neighbours.clear()
		self.log("Pinging for neighbours")
		cmd = message_encode(MSG_PING, 0, self.position, self.position)
		self.peerSocket.sendto(cmd, self.__mcastAddr)
	def pong(self, initor, addr):
		if initor == self.position:
			return
		self.log("Recieved ping from %s:%s, sending PONG" % (addr), 1)
		cmd = message_encode(MSG_PONG, 0, initor, self.position)
		self.peerSocket.sendto(cmd, addr)
	def moveNode(self):
		self.position = random_position(args.grid)
		self.log("Changed position to (%d,%d)" % self.position)



def main(mcast_addr,
	sensor_pos, sensor_range, sensor_val,
	grid_size, ping_period):
	"""
	mcast_addr: udp multicast (ip, port) tuple.
	sensor_pos: (x,y) sensor position tuple.
	sensor_range: range of the sensor ping (radius).
	sensor_val: sensor value.
	grid_size: length of the  of the grid (which is always square).
	ping_period: time in seconds between multicast pings.
	"""
	node = nodeContainer()
	# -- make sockets
	node.init(mcast_addr)
	# -- set node values
	node.position = sensor_pos
	node.range = sensor_range
	node.value = sensor_val
	node.pingTime = ping_period
	# -- create gui
	window = node.createWindow()
	# -- Command/message parser
	parser = msgParser(node)
	# -- Both peer and Mcast connections
	conns = node.getConnections()

	# -- This is the event loop
	while window.update():
		inputReady, outputReady, errorReady = \
			select.select(conns, [], [], 0)
		# Is it ping time already
		node.autoPing()

		# Network message
		for s in inputReady:
			parser.parseConnection(s)

		# Gui message
		line = window.getline()
		if line:
			parser.parseLine(line);

# -- program entry point
if __name__ == '__main__':
	import sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--group', help='multicast group', default='224.1.1.1')
	p.add_argument('--port', help='multicast port', default=1620, type=int)
	p.add_argument('--pos', help='x,y sensor position', default=None)
	p.add_argument('--grid', help='size of grid', default=100, type=int)
	p.add_argument('--range', help='sensor range', default=50, type=int)
	p.add_argument('--value', help='sensor value', default=-1, type=int)
	p.add_argument('--period', help='period between autopings (0=off)',
		default=30, type=int)
	args = p.parse_args(sys.argv[1:])
	if args.pos:
		pos = tuple( int(n) for n in args.pos.split(',')[:2] )
	else:
		pos = random_position(args.grid)
	if args.value >= 0:
		value = args.value
	else:
		value = randint(0, 100)
	mcast_addr = (args.group, args.port)
	main(mcast_addr, pos, args.range, value, args.grid, args.period)
