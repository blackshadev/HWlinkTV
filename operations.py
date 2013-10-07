class NOOP:
	@staticmethod
	def init(node):
		return 0
	@staticmethod
	def final(data, node):
		node.log("Received final echo back, op: %d, data: %d" % (0, data))
	@staticmethod
	def send(data, node):
		return data
	@staticmethod
	def reply(oldData, newData, node):
		return newData
	@staticmethod
	def emptyReply(op, newData, node):
		return 0

class SIZE:
	@staticmethod
	def init(node):
		return 1
	@staticmethod
	def final(data, node):
		node.log("The size of the network is %d" % data)
	@staticmethod
	def send(data, node):
		return 1
	@staticmethod
	def reply(oldData, newData, node):
		node.log("oldData: %d, newData: %d" % (oldData, newData))
		return oldData + newData
	@staticmethod
	def emptyReply(op, newData, node):
		return newData