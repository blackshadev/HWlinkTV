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
 - Echo's can be sent en recieved
TODO
 - Check if position is already taken
BUGS
 - Something is wrong at line 249
 - DistanceTo still malfunctions
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

def echoKey(seq, initor):
	return "%d,%d:%d" % (initor[0], initor[1], seq)

class msgParser:
	__node = None
	def __init__(self, node):
		self.__node = node
	def parseLine(self, line):
		if line == "ping":
			self.__node.ping()
		elif line == "list":
			self.__node.listNeighbours()
		elif line == "echo":
			self.__node.echoInit(0, 0)
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
		elif mType == MSG_ECHO:
			self.__node.echoRecieve(seq, initor, neighbour, op, data)
		elif mType == MSG_ECHO_REPLY:
			self.__node.echoReplyRecieve(seq, initor, neighbour, op, data)
		else:
			self.__node.log("Received %d from %s:%s on (%d,%d), unknown mType" \
				% (mType, addr[0], addr[1], neighbour[0], neighbour[1]))
		

class neighbours:
	__node = None
	__dict = {}
	def __init__(self, node):
		self.__node = node
	def __setitem__(self, pos, addr):
		self.__dict[pos] = addr
	def clear(self):
		self.__dict.clear()
	def __len__(self):
		return len(self.__dict)
	def __getitem__(self, key):
		return self.__dict[key]
	def forAll(self, fn):
		count = 0
		for key in self.__dict:
			fn(key, self.__dict[key])
			count += 1
		return count
	def __str__(self):
		import operator
		retr = "\n(x,y)\t\tDistance\t\taddress:port\n"
		for key in self.__dict:
			node = self.__dict[key]
			distance = self.__node.distanceTo(key)
			retr += "(%d,%d):\t\t%d\t\t%s:%s\n" % (key[0], key[1], distance, node[0], node[1], )
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

	__echoSeq = 0
	__echoPending = {}
	__echoFather = {}

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
			self.__neighbours[pos] = addr
			self.log("Found neighbour (%d,%d)" % pos)
	def listNeighbours(self):
		self.log("/-- Current known neighbours --\\")
		self.log(str(self.__neighbours))
		self.log("\\-- Current known neighbours --/")
	def inRange(self, pos):
		return self.distanceTo(pos) < self.range
	def distanceTo(self, pos):
		import math
		import operator
		diff = tuple(map(operator.div, pos, self.position))
		distance = math.sqrt(diff[0] ** 2 + diff[1] ** 2)
		return distance
	def moveNode(self):
		self.position = random_position(args.grid)
		self.log("Changed position to (%d,%d)" % self.position)
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
	""" Echo operations """
	def echoInit(self, op=0, data=0):
		self.__echoSeq += 1
		
		self.log("Sending echo wave with sequence number %d" % self.__echoSeq)

		self.echoSend(self.__echoSeq, self.position, op, data)
	def echoSend(self, seq, initor, op, data, excl=(-1,-1)):
		key = echoKey(seq, initor)

		self.log(
			"Sending echo wave with sequence number %d , initiated by (%d,%d)" \
			% (seq, initor[0], initor[1]))
		cmd = message_encode(MSG_ECHO, seq, initor, self.position, op, data)

		# Count neighbours exept the father node
		self.__echoPending[key] = len(self.__neighbours)
		if excl[0] > -1 and excl[1] > -1:
			self.__echoPending[key] -= 1

		if self.__echoPending[key] < 1:
			self.echoReplySend(self.__echoFather[key], seq, \
				initor, self.position, op, data)

		def callback(pos, addr):
			if pos[0] == excl[0] and pos[1] == excl[1]:
				return
			self.log("Sending echo wave to %s:%s" % (addr), 1)
			self.peerSocket.sendto(cmd, addr)

		self.__neighbours.forAll(callback)
	def echoReplyRecieve(self, seq, initor, neighbour, op, data):
		key = echoKey(seq, initor)

		self.__echoPending[key] -= 1
		self.log("Recieved Echo_Reply from (%d, %d), left: %d" % \
			(neighbour[0], neighbour[1], self.__echoPending[key]) )
		if self.__echoPending[key] <= 0:
			fatherAddr = self.__echoFather[key]
			self.echoReplySend(fatherAddr, seq, initor, neighbour, op, data)
	def echoReplySend(self, addr, seq, initor, neighbour, op, data):
		key = echoKey(seq, initor)

		if initor[0] == self.position[0] and initor[1] == self.position[1]:
			self.echoFinal(seq, initor, neighbour, op, data)
			return

		self.log("Sending result to addr %s:%s)" % addr)

		cmd = message_encode(MSG_ECHO_REPLY, seq, initor, self.position, op, data)
		# Something is wrong here
		self.peerSocket.sendto(cmd, addr)
	def echoFinal(self, seq, initor, neighbour, op, data):
		self.log("Recieved final echo back, op: %d, data: %d" % (op, data))
	def echoRecieve(self, seq, initor, neighbour, op, data):
		key = echoKey(seq, initor)

		# Already recieved Echo
		if key in self.__echoFather or (initor[0] == self.position[0] and initor[1] == self.position[1]):
			self.echoReplySend(self.__neighbours[neighbour], seq, initor, \
				neighbour, op, data)
			return

		# Add to recieved echo's
		self.__echoFather[key] = neighbour

		self.log(
			("Recieved echo wave with sequence number %d initiated by (%d,%d)"+\
			"from (%d,%d)") %\
			(seq, initor[0], initor[1], neighbour[0], neighbour[1]))
		# Sent it foward
		self.echoSend(seq, initor, op, data, excl=neighbour)



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
		default=0, type=int)
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
