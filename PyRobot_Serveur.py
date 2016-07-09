import socket, sys, subprocess
import RPi.GPIO as GPIO

from FrontLight import FrontLight
from MCP3008 import MCP3008

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)	

class PyRobot_Serveur:

	# Modules (Capteurs , éclairage, etc)
	FrontLight = FrontLight(4, 0) # pin, luminosity(%)
	MCP3008 = MCP3008(12, 16, 20, 21) # CLK, MOSI, MISO, CS

	def __init__(self, port):
		self.hote = ''
		self.port = port

	def start(self):

		self.serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serveur_socket.bind((self.hote, self.port))
		self.serveur_socket.listen(5)
		
		while True:
			print("Server listening at {}".format(self.port))

			try:
				self.client_socket, self.infos_connexion = self.serveur_socket.accept()
				self.tcp_read()
			except BrokenPipeError:
				self.close()
			finally:
				print("Connection closed.")
				self.client_socket.close()
				GPIO.cleanup()

	def tcp_read(self):
		msg_recu = ""
		while msg_recu != "bye":
			msg_recu = self.client_socket.recv(1024).decode("utf-8")
			if msg_recu != "":
				print(msg_recu)
				self.execute_cmd(msg_recu)
				#self.tcp_send(msg_recu)
			else: break
				
	def tcp_send(self, msg):
		self.client_socket.send(bytes(msg, 'utf-8'))

	def close(self):
		self.serveur_socket.close()
		GPIO.cleanup()

	def execute_cmd(self, cmd):
		tokens = cmd.split(" ")

		if tokens[0] == "red":
			subprocess.Popen(["python3", "LED_RGB.py", "255", "0", "0"])

		elif tokens[0] == "green":
			subprocess.Popen(["python3", "LED_RGB.py", "0", "255", "0"])

		elif tokens[0] == "blue":
			subprocess.Popen(["python3", "LED_RGB.py", "0", "0", "255"])

		elif tokens[0] == "rgb":
			if len(tokens) > 3:
				subprocess.Popen(["python3", "LED_RGB.py", tokens[1], tokens[2], tokens[3]])

		elif tokens[0] == "lg":
			if len(tokens) > 1:

				if tokens[1] == "on":
					self.FrontLight.on()
				elif tokens[1] == "off":
					self.FrontLight.off()

				try:
					self.FrontLight.setLuminosity(int(tokens[1]))
				except:
					pass

		elif tokens[0] == "flash":
			if len(tokens) > 1:
				subprocess.Popen(["python3", "FrontLight.py", "4", "100", tokens[1]])

		elif tokens[0] == "mcpr":
			if len(tokens) > 1:
				print("read")
					

if __name__ == "__main__":
	PyRobot_Serveur = PyRobot_Serveur(12800)
	PyRobot_Serveur.start()