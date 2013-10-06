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
 - Echo's
 - DistanceTo calculation
TODO
 - Check if position is already taken
 - Check for a better way to compare tuples and calculating with them
BUGS
 - Needs more testing
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
	"""
	Wrapper class to handle window and network input/commands
	"""
	__node = None
	def __init__(self, node):
		self.__node = node
	"""
	Window commands
	"""
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
	"""
	Network commands,
	 - Gets the message and sender address
	 - Decodes the message
	 - Decides what to do based upon the mType
	"""
	def parseSensorMessage(self, conn):
		raw, addr = conn.recvfrom(1024)
		mType, seq, initor, neighbour, op, data = message_decode(raw)
		if mType == MSG_PING:
			self.__node.pong(initor, addr)
		elif mType == MSG_PONG:
			self.__node.addNeighbour(neighbour, addr)
		elif mType == MSG_ECHO:
			self.__node.echoReceive(seq, initor, neighbour, op, data)
		elif mType == MSG_ECHO_REPLY:
			self.__node.echoReplyReceive(seq, initor, neighbour, op, data)
		else:
			self.__node.log("Received %d from %s:%s on (%d,%d), unknown mType" \
				% (mType, addr[0], addr[1], neighbour[0], neighbour[1]))
		

class neighbours:
	"""
	Neighbours wrapper / dictionary
	Differences from a standard dict:
	 - Bounded to a node (for distance calculations)
	 - The "toString" returns a table of neighbours and the distance to them
	 - The forAll function executes a function for all nodes
	"""
	__node = None
	__dict = {}
	def __init__(self, node):
		self.__node = node
	def clear(self):
		self.__dict.clear()
	def __len__(self):
		return len(self.__dict)
	def __getitem__(self, key):
		return self.__dict[key]
	def __setitem__(self, pos, addr):
		self.__dict[pos] = addr
	def forAll(self, fn):
		count = 0
		for key in self.__dict:
			fn(key, self.__dict[key])
			count += 1
		return count
	def __str__(self):
		retr = "\n(x,y)\t\tDistance\t\taddress:port\n"
		for key in self.__dict:
			node = self.__dict[key]
			distance = self.__node.distanceTo(key)
			retr += "(%d,%d):\t\t%d\t\t%s:%s\n" % (key[0], key[1], distance, node[0], node[1], )
		return retr
		

class nodeContainer:
	"""
	Node wrapper
	Contains all functions and data of the node.
	"""
	__neighbours = None
	__window = None
	__debug = 1
	
	# Socket variables
	__host = ''
	__mcastAddr = None
	address = None
	peerSocket = None
	mcastSocket = None

	# Node values
	position = None
	value = None
	range = 50
	pingTime = 30 
	__lastPing = 0

	# EchoWave variables
	__echoSeq = 0
	__echoPending = {}
	__echoFather = {}

	"""
	Creates a node, with:
	 - mcast listener socket for pings multicasts
	 - peerSocket for node to node connection
	 - neighbours object to keep track of the neighbours 
	"""
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
	""" Return both sockets in an array """
	def getConnections(self):
		return [self.mcastSocket, self.peerSocket]
	""" Create the GUI window """
	def createWindow(self):
		window = MainWindow()
		window.writeln( 'my address is %s:%s' % self.address )
		window.writeln( 'my position is (%s, %s)' % self.position )
		window.writeln( 'my sensor value is %s' % self.value )
		self.__window = window
		return window
	""" Display a message on the window """
	def log(self, msg, level=0):
		if self.__debug > level:
			timeStr = time.strftime("%H:%M:%S")
			self.__window.writeln("[%s]: %s" % (timeStr, msg))
	""" --- Neighbour operations --- """
	""" Add a neighbour """
	def addNeighbour(self, pos, addr):
		self.log("Received PONG from %s:%s at (%d,%d) " \
			% (addr[0], addr[1], pos[0], pos[1]), 1)
		if self.inRange(pos):
			self.__neighbours[pos] = addr
			self.log("Found neighbour (%d,%d)" % pos)
	""" Log a list of all neighbours """
	def listNeighbours(self):
		self.log("/-- Current known neighbours --\\")
		self.log(str(self.__neighbours))
		self.log("\\-- Current known neighbours --/")
	""" Returns if the given position is in range of the node """
	def inRange(self, pos):
		return self.distanceTo(pos) < self.range
	""" Calculates the distance to the given position """
	def distanceTo(self, pos):
		import math
		diff = (self.position[0] - pos[0], self.position[1] - pos[1])
		
		return math.sqrt(diff[0] ** 2 + diff[1] ** 2)
	""" Move the node to a random position """
	def moveNode(self):
		self.position = random_position(args.grid)
		self.log("Changed position to (%d,%d)" % self.position)
	""" --- Protocol operations --- """
	""" Executes a ping if the pingTime has elapsed since the lastPing """
	def autoPing(self):
		if self.pingTime < 1:
			return
		if self.__lastPing + self.pingTime < time.time():
			self.ping()
			self.__lastPing = time.time()
	""" clear neighbours and pings to all nodes by multicasting """
	def ping(self):
		self.log("Cleared neighbour list", 1)
		self.__neighbours.clear()
		self.log("Pinging for neighbours")
		cmd = message_encode(MSG_PING, 0, self.position, self.position)
		self.peerSocket.sendto(cmd, self.__mcastAddr)
	""" Upon receiving a pong, add that node to its neighbours """
	def pong(self, initor, addr):
		if initor == self.position:
			return
		self.log("Received ping from %s:%s, sending PONG" % (addr), 1)
		cmd = message_encode(MSG_PONG, 0, initor, self.position)
		self.peerSocket.sendto(cmd, addr)
	""" --- Echo operations --- """
	""" Start an Echo Wave with given operation and starting data """
	def echoInit(self, op=0, data=0):
		self.__echoSeq += 1
		
		self.log("Sending echo wave with sequence number %d" % self.__echoSeq)

		self.echoSend(self.__echoSeq, self.position, op, data)
	""" 
	Send the EchoWave to all neighbours, 
	Setting the correct number of replys to wait for 
	"""
	def echoSend(self, seq, initor, op, data, excl=(-1,-1)):
		key = echoKey(seq, initor)

		self.log(
			"Sending echo wave with sequence number %d , initiated by (%d,%d)" \
			% (seq, initor[0], initor[1]))
		cmd = message_encode(MSG_ECHO, seq, initor, self.position, op, data)

		# Count neighbours except the father node
		self.__echoPending[key] = len(self.__neighbours)
		if excl[0] > -1 and excl[1] > -1:
			self.__echoPending[key] -= 1

		# No neighbours to sent to? Send a reply immidiately
		if self.__echoPending[key] < 1:
			self.echoReplySend(self.__echoFather[key], seq, \
				initor, self.position, op, data)

		""" Callback function for the actual sending """
		def callback(pos, addr):
			if pos[0] == excl[0] and pos[1] == excl[1]:
				return
			self.log("Sending echo wave to %s:%s" % (addr), 1)
			self.peerSocket.sendto(cmd, addr)

		self.__neighbours.forAll(callback)
	""" 
	Upon receiving a reply,
	 - Lower the amount of replys to wait for
	 - If their is nothing to wait for anymore:
	  - Goto echoFinal if this node is the initiator
	  - Else, send reply to father node.
	"""
	def echoReplyReceive(self, seq, initor, neighbour, op, data):
		key = echoKey(seq, initor)

		self.__echoPending[key] -= 1
		self.log("Received Echo_Reply from (%d, %d), left: %d" % \
			(neighbour[0], neighbour[1], self.__echoPending[key]) )
		if self.__echoPending[key] < 1:
			# Is own echo or sent it back to father
			if initor[0] == self.position[0] and initor[1] == self.position[1]:
				self.echoFinal(seq, initor, neighbour, op, data)
				return
			# Sent it to the father node
			fatherAddr = self.__echoFather[key]
			self.echoReplySend(fatherAddr, seq, initor, neighbour, op, data)
	""" Send an echo reply to the neighbour given in destPos """
	def echoReplySend(self, destPos, seq, initor, neighbour, op, data):
		addr = self.__neighbours[destPos]

		self.log("Sending EchoReply to addr %s:%s)" % addr)

		cmd = message_encode(MSG_ECHO_REPLY, seq, initor, self.position, op, data)
		self.peerSocket.sendto(cmd, addr)
	""" Puts the result of the on the screen """
	def echoFinal(self, seq, initor, neighbour, op, data):
		self.log("Received final echo back, op: %d, data: %d" % (op, data))
	""" 
	Upon receiving an Echo
	 - Decide if you alrady got this echoWave by checking if the combination
	   of initiator and sequence number already exists in the father dict
	 - Adds the given neighbour to the fatherDict with the given sequence number
	"""
	def echoReceive(self, seq, initor, neighbour, op, data):
		key = echoKey(seq, initor)

		# Already received Echo
		if key in self.__echoFather or (initor[0] == self.position[0] \
			and initor[1] == self.position[1]):
				self.echoReplySend(neighbour, seq, initor, neighbour, op, data)
				return

		# Adds the sequence number + initiator position in the dictionary 
		# with the neighbour as the father node
		self.__echoFather[key] = neighbour

		self.log(
			("Received echo wave with sequence number %d initiated by (%d,%d)"+\
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
			parser.parseSensorMessage(s)

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
