"""
Classes in this file define the behaviour of that operation.
These operators still need to be called upon, this is done by the 
Operations::getFn method in lab4.~.py
"""

class NOOP:
	""" Starting value of data """
	@staticmethod
	def init(node):
		return 0
	""" What needs to be done after the echo wave """
	@staticmethod
	def final(data, node):
		node.log("Received final echo back, op: %d, data: %d" % (0, data))
	""" The data send to an father node, with data the current data """
	@staticmethod
	def send(data, node):
		return data
	""" 
	The data after receiving a reply, 
	 - oldData the current known data,
	 - newData the received data
	 the return value becomes the new newData, which will be sent back if
	 no more replies are expected
	 """
	@staticmethod
	def reply(oldData, newData, node):
		return newData
	""" Data send with a emptyReply (when a node already received that echo) """
	@staticmethod
	def emptyReply(newData, node):
		return 0

class SIZE:
	@staticmethod
	def init(node):
		return 0
	@staticmethod
	def final(data, node):
		node.log("The size of the network is %d" % (data + 1))
	@staticmethod
	def send(data, node):
		return 1 + data
	@staticmethod
	def reply(oldData, newData, node):
		node.log("oldData: %d, newData: %d, result: %s" % (oldData, newData, oldData + newData), 1)
		return oldData + newData
	@staticmethod
	def emptyReply(newData, node):
		return 0

class MAX:
	@staticmethod
	def init(node):
		return node.value
	@staticmethod
	def final(data, node):
		node.log("The maximum value in the network is %d" % data)
	@staticmethod
	def send(data, node):
		return max(data, node.value)
	@staticmethod
	def reply(oldData, newData, node):
		if newData == -1:
			return oldData
		new = max(oldData, newData)
		node.log("oldMax: %d, maybe: %d, new: %d" % (oldData, newData, new),1)
		return new
	@staticmethod
	def emptyReply(newData, node):
		return -1

class MIN:
	@staticmethod
	def init(node):
		return node.value
	@staticmethod
	def final(data, node):
		node.log("The minimum value in the network is %d" % data)
	@staticmethod
	def send(data, node):
		return min(data, node.value)
	@staticmethod
	def reply(oldData, newData, node):
		if newData == -1:
			return oldData
		new = min(oldData, newData)
		node.log("oldMin: %d, maybe: %d, new: %d" % (oldData, newData, new),1)
		return new
	@staticmethod
	def emptyReply(newData, node):
		return -1

class SUM:
	@staticmethod
	def init(node):
		return 0
	@staticmethod
	def final(data, node):
		node.log("The total sum of the network is %d" % (data + node.value))
	@staticmethod
	def send(data, node):
		return data + node.value
	@staticmethod
	def reply(oldData, newData, node):
		if newData == -1:
			return oldData
		new = oldData + newData
		node.log("old: %d, new: %d, sum: %d" % (oldData, newData, new),1)
		return new
	@staticmethod
	def emptyReply(newData, node):
		return -1