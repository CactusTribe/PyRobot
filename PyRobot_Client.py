import socket

class PyRobot_Client:

	def __init__(self, hote, port):
		self.hote = hote
		self.port = port
		self.connected = False

	def start(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(0.5)

		try:
			self.socket.connect((self.hote, self.port))
			print("Connected at {}:{}".format(self.hote, self.port))
			self.connected = True
		except:
			self.close()

	def tcp_read(self):
		return self.socket.recv(1024).decode("utf-8")	

	def tcp_send(self, msg):
		self.socket.send(msg.encode("utf-8"))

	def close(self):
		self.connected = False
		self.socket.close()

if __name__ == "__main__":

	PyRobot_Client = PyRobot_Client("localhost", 12800)
	PyRobot_Client.start()

	msg = ""
	while msg != "bye":
		msg = input("> ")
		PyRobot_Client.tcp_send(msg)
		msg_recu = PyRobot_Client.tcp_read()

		if msg_recu != "":
			print(msg_recu)
		else: 
			PyRobot_Client.close()
			break


