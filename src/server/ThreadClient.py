import socket, threading

class ThreadClient(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.clients = None
		self.connection = None

	def run(self):
		self.setName(self.name)
		nom = self.getName()

		while True:
			msg_recu = self.connection.recv(1024).decode("utf-8")			
			if msg_recu != "":
				self.execute_cmd(msg_recu)
			else: break

		del self.clients[nom]
		print(" x {} at {} disconnected.".format(self.name, self.connection.getsockname()))
		self.connection.close()


	# Send message to client
	def tcp_send(self, msg):
		self.connection.send(bytes(msg, 'utf-8'))

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]