import socket, sys, subprocess, time
import RPi.GPIO as GPIO

from FrontLight import FrontLight
from MCP3008 import MCP3008

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)	

class PyRobot_Serveur:

	GPIO.cleanup()

	# Modules (Capteurs , éclairage, etc)
	FrontLight = FrontLight(4)        	# PIN
	MCP3008 = MCP3008(12, 16, 20, 21) 	# CLK, MOSI, MISO, CS

	# Constructor
	def __init__(self, port):
		self.hote = ''
		self.port = port

	# Starting server
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

	# Close server
	def close(self):
		self.serveur_socket.close()
		GPIO.cleanup()

	# Read loop
	def tcp_read(self):
		while True:
			msg_recu = self.client_socket.recv(1024).decode("utf-8")			
			if msg_recu != "":
				print(msg_recu)
				self.execute_cmd(msg_recu)
			else: break
				
	# Send message to client
	def tcp_send(self, msg):
		self.client_socket.send(bytes(msg, 'utf-8'))

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]

		if cmd == "sled":
			self.StatusLED_Module(args)

		elif cmd == "fl":
			self.FrontLight_Module(args)

		elif cmd == "sns":
			self.Sensors_Module(args)

	# --------------------------------------------
	# MODULE FRONT-LIGHTS
	# --------------------------------------------
	def FrontLight_Module(self, args):
		try:

			if args[1] == "on":
				self.FrontLight.on()

			elif args[1] == "off":
				self.FrontLight.off()

			elif args[1] == "lum":
				self.FrontLight.setLuminosity(int(args[2]))

			elif args[1] == "flash":
				subprocess.Popen(["python3", "FrontLight.py", "4", args[2]])
				
			elif args[1] == "status":
				self.tcp_send("fl status {} {}".format(self.FrontLight.isOn(), self.FrontLight.luminosity))

		except: pass

	# --------------------------------------------
	# MODULE STATUS-LED
	# --------------------------------------------
	def StatusLED_Module(self, args):
		try:

			if args[1] == "red":
				subprocess.Popen(["python3", "LED_RGB.py", "255", "0", "0"])

			elif args[1] == "green":
				subprocess.Popen(["python3", "LED_RGB.py", "0", "255", "0"])

			elif args[1] == "blue":
				subprocess.Popen(["python3", "LED_RGB.py", "0", "0", "255"])

			elif args[1] == "rgb":
				subprocess.Popen(["python3", "LED_RGB.py", args[2], args[3], args[4]])

		except: pass

	# --------------------------------------------
	# MODULE SENSORS
	# --------------------------------------------
	def Sensors_Module(self, args):
		try:

			if len(args) > 1:
				start = time.time()
				elapsed = 0
				timer = 12

				while True:
					value = self.MCP3008.getValue(int(args[1]))
					self.tcp_send("sns "+args[1]+" "+str(value))
					time.sleep(0.5) 

					elapsed = time.time() - start
					if elapsed >= timer:
						break

			else:
				values = [] 
				for e in range(8):
					values += [self.MCP3008.getValue(e)]

				self.tcp_send("sns {} {} {} {} {} {} {} {}".format(values[0], values[1], values[2], values[3],
					values[4], values[5], values[6], values[7]))

		except: pass


if __name__ == "__main__":
	PyRobot_Serveur = PyRobot_Serveur(12800)
	try:
		PyRobot_Serveur.start()
	except Exception as e:
		print(str(e))
		PyRobot_Serveur.close()