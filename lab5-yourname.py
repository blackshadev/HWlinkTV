## Netwerken en Systeembeveiliging Lab 5 - Distributed Sensor Network
## NAME:
## STUDENT ID:
"""
DONE
 - The mcastSocket is only a listener
 - All messages are send with the peerSocket
 - Ping Pong works
TODO
 - Ping interval
 - distance calculation function in nodeContainer
 - Check working
BUGS
 - Node still sends to it self (no?)
"""
import sys
import struct
import select
from socket import *
from random import randint
from gui import MainWindow
from sensor import *


# Get random position in NxN grid.
def random_position(n):
	x = randint(0, n)
	y = randint(0, n)
	return (x, y)

class msgParser:
	__node = None
	__widow = None
	def __init__(self, node, window):
		self.__node = node
		self.__window = window
	def parseLine(self, line):
		if line == "ping":
			self.__node.ping()
		self.__window.writeln(line)
	def parseConnection(self, conn):
		if conn == self.__node.mcastSocket:
			self.parseMcast(conn)
		else:
			self.parsePeer(conn)
	def parseMcast(self, conn):
		raw, addr = conn.recvfrom(1024)
		mType, seq, initor, neighbour, op, data = message_decode(raw)
		print "Mcast Got %d from %s" % (mType, str(addr))
		if mType == MSG_PING:
			self.__node.pong(initor, addr)
	def parsePeer(self, conn):
		raw, addr = conn.recvfrom(1024)
		mType, seq, initor, neighbour, op, data = message_decode(raw)
		print "peer Got %d from %s" % (mType, str(addr))
		if mType == MSG_PONG:
			self.__node.addNeighbour(neighbour, addr)


class neighbours:
	__node = None
	__dict = {}
	def __init__(self, node):
		self.__node = node
	def confirm(self, pos, addr):
		import operator
		diff = tuple(map(operator.div, pos, self.__node.position))
		print diff
		distance = diff[0] ** 2 + diff[1] ** 2
		print distance
		inrange = distance < self.__node.range ** 2 and distance != 0
		if inrange:
			self.__dict[pos] = addr
			print "tvged"
			print self.__dict
		else:
			print "NOPS"
		

class nodeContainer:
	"""
	Node wrapper
	"""
	__host = ''
	__mcastAddr = None
	__neighbours = None
	address = None
	peerSocket = None
	mcastSocket = None

	position = None
	value = None
	range = 50
	pingTime = 30

	def __init__(self):
		# Multicast listener socket
		self.mcastSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.mcastSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

		# Peer socket
		self.peerSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.peerSocket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 5)
		
		self.__host = ''
		self.__neighbours = neighbours(self)
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
	def addNeighbour(self, pos, addr):
		self.__neighbours.confirm(pos, addr)
	def ping(self):
		cmd = message_encode(MSG_PING, 0, self.position, self.position)
		self.peerSocket.sendto(cmd, self.__mcastAddr)
	def pong(self, initor, addr):
		if addr == self.address:
			print "Own node"
			return False
		print "sending pong %s" % str(addr)
		print self.address
		cmd = message_encode(MSG_PONG, 0, initor, self.position)
		self.peerSocket.sendto(cmd, addr)


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
	node.init(mcast_addr)
	node.position = sensor_pos
	node.range = sensor_range
	node.value = sensor_val
	node.pingTime = ping_period

	# -- make the gui --
	window = MainWindow()
	window.writeln( 'my address is %s:%s' % node.address )
	window.writeln( 'my position is (%s, %s)' % node.position )
	window.writeln( 'my sensor value is %s' % node.value )

	parser = msgParser(node, window)
	conns = node.getConnections()

	# -- This is the event loop. --
	while window.update():
		inputReady, outputReady, errorReady = \
			select.select(conns, [], [], 0)

		for s in inputReady:
			parser.parseConnection(s)

		line = window.getline()
		if line:
			parser.parseLine(line);

# -- program entry point --
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
