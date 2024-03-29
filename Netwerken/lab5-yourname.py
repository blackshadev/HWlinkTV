"""
Netwerken en Systeembeveiliging Lab 5 - Distributed Sensor Network
Authors: Tessa Klunder, Vincent Hagen
UvAIDs: ......, 10305602
"""
import sys
import struct
import select
from socket import *
from random import randint
from gui import MainWindow
from sensor import *
import time
import re


# Get random position in NxN grid.
def random_position(n):
	x = randint(0, n)
	y = randint(0, n)
	return (x, y)


class msgParser:
	"""
	Wrapper class to handle window and network input/commands
	"""
	def __init__(self, node):
		self.__node = node
	"""
	Window commands
	"""
	def parseLine(self, line):
		self.__node.log(line)
		cmd = line.split(' ')[0]
		if cmd == "ping":
			self.__node.ping()
		elif cmd == "list":
			self.__node.listNeighbors()
		elif cmd == "echo":
			self.__node.echoInit(OP_NOOP)
		elif cmd == "size":
			self.__node.echoInit(OP_SIZE)
		elif cmd == "max":
			self.__node.echoInit(OP_MAX)
		elif cmd == "min":
			self.__node.echoInit(OP_MIN)
		elif cmd == "sum":
			self.__node.echoInit(OP_SUM)
		elif cmd == "move":
			self.__node.moveNode(line)
		elif cmd == "debug":
			self.__node.debugMode(line)
		elif cmd == "value":
			self.__node.valueNode(line)
		elif cmd == "help":
			self.__node.helpList()
		else:
			self.__node.log("No command for %s, type 'help' for a list of commands" % cmd)
	"""
	Network commands,
	 - Gets the message and sender address
	 - Decodes the message
	 - Decides what to do based upon the mType
	"""
	def parseSensorMessage(self, conn):
		raw, addr = conn.recvfrom(1024)
		mType, seq, initor, neighbor, op, data = message_decode(raw)
		if mType == MSG_PING:
			self.__node.pong(initor, addr)
		elif mType == MSG_PONG:
			self.__node.addNeighbor(neighbor, addr)
		elif mType == MSG_ECHO:
			self.__node.echoReceive(addr, seq, initor, neighbor, op, data)
		elif mType == MSG_ECHO_REPLY:
			self.__node.echoReplyReceive(seq, initor, neighbor, op, data)
		else:
			self.__node.log("Received %d from %s:%s on (%d,%d), unknown mType" \
				% (mType, addr[0], addr[1], neighbor[0], neighbor[1]))
		

class neighbors:
	"""
	Neighbors wrapper / dictionary
	Differences from a standard dict:
	 - Bounded to a node (for distance calculations)
	 - The "toString" returns a table of neighbors and the distance to them
	 - The forAll function executes a function for all nodes
	"""
	def __init__(self, node):
		self.__node = node
		self.__dict = {}
	def clear(self):
		self.__dict.clear()
	def __len__(self):
		return len(self.__dict)
	def __getitem__(self, key):
		if key not in self.__dict:
			self.__node.log("Neighbor %d,%d not found", key)
		return self.__dict[key]
	def __setitem__(self, pos, addr):
		self.__dict[pos] = addr
	def __contains__(self, key):
		return key in self.__dict
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

""" Operation wrappers, getFn gives the function defined by the given operation
	and the fnName """
class Operations:
	__map = ['NOOP', 'SIZE', 'SUM', 'MIN', 'MAX']
	@staticmethod
	def getFn(op, fnName):
		import operations
		return getattr(getattr(operations, Operations.__map[op]), fnName)

""" Wrapper class for an EchoWave """
class EchoWave:
	def __init__(self, value, father, pending):
		self.father = father
		self.value = value
		self.pending = pending
	# Calculate the echoKey of an EchoWave
	@staticmethod
	def echoKey(seq, initor):
		return "%d,%d:%d" % (initor[0], initor[1], seq)

"""
Node wrapper
Contains all functions and data of the node.
"""
class nodeContainer:

	"""
	Creates a node, with:
	 - mcast listener socket for pings multicasts
	 - peerSocket for node to node connection
	 - neighbors object to keep track of the neighbors 
	"""
	def __init__(self):
		# Multicast listener socket
		self.mcastSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.mcastSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

		# Peer socket
		self.peerSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.peerSocket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 5)
		
		# Defaults
		self.__debug = 1
		self.__host = ''
		self.__neighbors = neighbors(self)
		self.__lastPing = 0

		# Echo wave defaults
		self.__echoWaves = {}
		self.__echoSeq = 0
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
	def setWindow(self, window):
		window.writeln( 'my address is %s:%s' % self.address )
		window.writeln( 'my position is (%s, %s)' % self.position )
		window.writeln( 'my sensor value is %s' % self.value )
		self.__window = window
	""" Display a message on the window """
	def log(self, msg, level=0):
		if self.__debug > level:
			timeStr = time.strftime("%H:%M:%S")
			self.__window.writeln("[%s]: %s" % (timeStr, msg))
	""" Turn debug mode on/off """
	def debugMode(self, line):
		if line == "debug on":
			if self.__debug == 2:
				self.log("Already in debug mode")
			else:
				self.__debug = 2
				self.log("Entered debug mode")
		elif line == "debug off":
			if self.__debug != 2:
				self.log("Not in debug mode")
			else:
				self.__debug = 1
				self.log("Exited debug mode")
		else:
			self.log("No command for %s, use: 'debug [on/off]'" % line)
	""" List all commands """
	def helpList(self):
		logStr = "/-- List of commands --\\\n"
		logStr += "ping\t\tSends a multicast ping message\n" \
			"list\t\tLists all known neighbors\n" \
			"move [x y]\t\tMoves the node by choosing a new position randomly\n" \
			"echo\t\tInitiates an echo wave\n" \
			"size\t\tComputes the size of the network\n" \
			"value [value]\t\tThe node chooses a new random sensor value\n" \
			"sum\t\tComputes the sum of all sensor values\n" \
			"min\t\tComputes the minimum of all sensor values\n" \
			"max\t\tComputes the maximum of all sensor values\n" \
			"debug [on/off]\t\tEnables debugging logs\n"
		logStr += "\\-- List of commands --/"
		self.log(logStr)
	""" --- Neighbor operations --- """
	""" Add a neighbor """
	def addNeighbor(self, pos, addr):
		self.log("Received PONG from %s:%s at (%d,%d) " \
			% (addr[0], addr[1], pos[0], pos[1]), 1)
		if self.inRange(pos):
			self.__neighbors[pos] = addr
			self.log("Found neighbor (%d,%d)" % pos, 1)
	""" Log a list of all neighbors """
	def listNeighbors(self):
		logStr = "/-- Current known neighbors --\\\n"
		logStr += str(self.__neighbors)
		logStr += "\\-- Current known neighbors --/"
		self.log(logStr)
	""" Returns if the given position is in range of the node """
	def inRange(self, pos):
		return self.distanceTo(pos) < self.range
	""" Calculates the distance to the given position """
	def distanceTo(self, pos):
		import math
		diff = (self.position[0] - pos[0], self.position[1] - pos[1])
		
		return math.sqrt(diff[0] ** 2 + diff[1] ** 2)
	""" Move the node to a position, if no position given, than random """
	def moveNode(self, line):
		matches = re.search('move\s(\d+)(?:,|\s)+(\d+).*', line)

		if matches != None:
			x, y = (min(int(matches.group(1)), args.grid),\
				min(int(matches.group(2)), args.grid))
			self.position = (x,y)
		else:
			self.position = random_position(args.grid)
		self.log("Changed position to (%d,%d)" % self.position)
	""" Change the value of the node """
	def valueNode(self, line):
		matches = re.search('value\s(\d*).*', line)

		if matches != None:
			self.value = int(matches.group(1))
		else:
			self.value = randint(0, 100)
		self.log("Changed value to %d" % self.value)
	""" --- Protocol operations --- """
	""" Executes a ping if the pingTime has elapsed since the lastPing """
	def autoPing(self):
		if self.pingTime < 1:
			return
		if self.__lastPing + self.pingTime < time.time():
			self.ping()
			self.__lastPing = time.time()
	""" clear neighbors and pings to all nodes by multicasting """
	def ping(self):
		self.log("Cleared neighbor list", 1)
		self.__neighbors.clear()
		self.log("Pinging for neighbors", 1)
		cmd = message_encode(MSG_PING, 0, self.position, self.position)
		self.peerSocket.sendto(cmd, self.__mcastAddr)
	""" Upon receiving a pong, add that node to its neighbors """
	def pong(self, initor, addr):
		if initor == self.position:
			return
		self.log("Received ping from %s:%s, sending PONG" % (addr), 1)
		cmd = message_encode(MSG_PONG, 0, initor, self.position)
		self.peerSocket.sendto(cmd, addr)
	""" --- Echo operations --- """
	""" Start an Echo Wave with given operation and starting data """
	def echoInit(self, op=0):
		self.__echoSeq += 1
		key = EchoWave.echoKey(self.__echoSeq, self.position)
		
		self.log("Sending echo wave with sequence number %d" % self.__echoSeq, 1)

		opFn = Operations.getFn(op, "init")
		self.__echoWaves[key] = EchoWave(opFn(self), None, len(self.__neighbors))

		self.echoSend(self.__echoSeq, self.position, op)
	""" 
	Send the EchoWave to all neighbors, 
	Setting the correct number of replys to wait for 
	"""
	def echoSend(self, seq, initor, op, excl=(-1,-1)):
		key = EchoWave.echoKey(seq, initor)

		data = self.__echoWaves[key].value

		self.log(
			("Sending echo wave with sequence number %d , initiated by (%d,%d)"+\
			" op: %d, data: %d"
			)% (seq, initor[0], initor[1], op, data), 1)
		cmd = message_encode(MSG_ECHO, seq, initor, self.position, op, data)

		if excl[0] > -1 and excl[1] > -1:
			self.__echoWaves[key].pending -= 1

		# No neighbors to sent to? Send a reply immidiately
		if self.__echoWaves[key].pending < 1:
			if self.__echoWaves[key].father != None:
				self.echoReplySend(seq, initor, self.position, op)
			else:
				self.echoFinal(seq, initor, op)

		""" Callback function for the actual sending """
		def callback(pos, addr):
			if pos[0] == excl[0] and pos[1] == excl[1]:
				return
			self.log("Sending echo wave to %s:%s" % (addr), 1)
			self.peerSocket.sendto(cmd, addr)

		self.__neighbors.forAll(callback)
	""" 
	Upon receiving a reply,
	 - Lower the amount of replys to wait for
	 - If their is nothing to wait for anymore:
	  - Goto echoFinal if this node is the initiator
	  - Else, send reply to father node.
	"""
	def echoReplyReceive(self, seq, initor, neighbor, op, data):
		key = EchoWave.echoKey(seq, initor)

		self.__echoWaves[key].pending -= 1
		opFn = Operations.getFn(op, "reply")
		self.__echoWaves[key].value = opFn(self.__echoWaves[key].value, data, self)

		self.log("Received Echo_Reply from (%d, %d) op: %d, data: %d, left: %d"\
			% (neighbor[0], neighbor[1], op, data, \
				self.__echoWaves[key].pending), 1)

		if self.__echoWaves[key].pending < 1:
			# Is own echo or sent it back to father
			if initor[0] == self.position[0] and initor[1] == self.position[1]:
				self.echoFinal(seq, initor, op)
				return
			# Sent it to the father node
			self.echoReplySend(seq, initor, neighbor, op)
	"""
	Send an empty echo reply to "toAddr", if the EchoWave is already
	Kown, the operators emptyReply method gets the known data, else None
	"""
	def echoReplySendEmpty(self, toAddr, seq, initor, neighbor, op):
		key = EchoWave.echoKey(seq, initor)

		data = None
		if key in self.__echoWaves:
			data = self.__echoWaves[key].value
		opFn = Operations.getFn(op, 'emptyReply')
		data = opFn(data, self)

		self.log("Sending EchoReply to addr %s:%s with op: %d, data: %d" %\
			(toAddr[0], toAddr[1], op, data ), 1)

		cmd = message_encode(MSG_ECHO_REPLY, seq, initor, self.position, op, data)
		self.peerSocket.sendto(cmd, toAddr)
	""" Send a echoReply to the father node """
	def echoReplySend(self, seq, initor, neighbor, op):
		key = EchoWave.echoKey(seq, initor)
		father = self.__echoWaves[key].father
		fatherAddr = self.__neighbors[father]

		data = self.__echoWaves[key].value
		opFn = Operations.getFn(op, 'send')
		data = opFn(data, self)

		self.log("Sending EchoReply to addr %s:%s with op: %d, data: %d" %\
			(fatherAddr[0], fatherAddr[1], op, data ), 1)

		cmd = message_encode(MSG_ECHO_REPLY, seq, initor, self.position, op, data)
		self.peerSocket.sendto(cmd, fatherAddr)
	""" Puts the result of the on the screen """
	def echoFinal(self, seq, initor, op):
		key = EchoWave.echoKey(seq, initor)
		data = self.__echoWaves[key].value

		opFn = Operations.getFn(op, "final")
		opFn(data, self)

		self.log("Received final echo back, op: %d, data: %d" % (op, data), 1)
	""" 
	Upon receiving an Echo
	 - Decide if you alrady got this echoWave by checking if the combination
	   of initiator and sequence number already exists in the father dict
	 - Adds the given neighbor to the fatherDict with the given sequence number
	"""
	def echoReceive(self, fromAddr, seq, initor, neighbor, op, data):
		key = EchoWave.echoKey(seq, initor)

		# Send empty reply back to sender when: EchoWave already received,
		# the sending node is not a known neighbor
		if key in self.__echoWaves or neighbor not in self.__neighbors:

				self.echoReplySendEmpty(fromAddr, seq, initor, neighbor, op)
				return

		# Adds the sequence number + initiator position in the dictionary 
		# with the neighbor as the father node
		self.__echoWaves[key] = EchoWave(data, neighbor, len(self.__neighbors))

		self.log(
			("Received echo wave with sequence number %d initiated by (%d,%d)"+\
			"from (%d,%d)") %\
			(seq, initor[0], initor[1], neighbor[0], neighbor[1]), 1)
		# Sent it foward
		self.echoSend(seq, initor, op, excl=neighbor)



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
	window = MainWindow()
	node.setWindow(window)
	# -- Command/message parser
	parser = msgParser(node)
	# -- Both peer and Mcast connections
	conns = node.getConnections()

	# -- This is the event loop
	while window.update():
		inputReady, outputReady, errorReady = \
			select.select(conns, [], [], 0.025)
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
		default=5, type=int)
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
