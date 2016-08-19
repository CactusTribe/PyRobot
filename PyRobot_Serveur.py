import socket, sys, subprocess, time, threading
import RPi.GPIO as GPIO

from FrontLight import FrontLight
from MCP3008 import MCP3008
from LED_RGB import LED_RGB
from Motor_DC import Motor_DC
from MQ_XX import MQ_XX

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)	

closed = True

class PyRobot_Serveur:

	GPIO.cleanup()

	# Modules (Capteurs , éclairage, etc)
	FrontLight = FrontLight(4)        	# PIN
	MCP3008 = MCP3008(12, 16, 20, 21) 	# PIN : CLK, MOSI, MISO, CS
	StatusLED = LED_RGB(22, 27, 17)

	Motor_L = Motor_DC(13, 19, 26) 			# PIN : SPEED, FW, BW
	Motor_R = Motor_DC(23, 24, 25)			# PIN : SPEED, FW, BW

	# GAS SENSORS
	MQ_2 = MQ_XX(0, 5, 9.83) # PIN, RESISTANCE, CLEAN_AIR_FACTOR


	# Constructor
	def __init__(self, port):
		self.hote = ''
		self.port = port

		self.setup()

	def setup(self):
		# CALIBRATION SENSORS ------------------------
		self.MQ_2.MQCalibration()


	# Starting server
	def start(self):
		global closed

		self.serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serveur_socket.bind((self.hote, self.port))
		self.serveur_socket.listen(5)
		
		while True:
			print("Server listening at {}".format(self.port))

			try:
				self.client_socket, self.infos_connexion = self.serveur_socket.accept()
				closed = False
				ThreadEvent = threading.Thread(target = self.eventLoop, args = [] )
				ThreadEvent.start()

				self.tcp_read()

			except BrokenPipeError:
				self.close()
			finally:
				print("Connection closed.")
				self.client_socket.close()
				self.FrontLight.off()
				closed = True

	# Close server
	def close(self):
		global closed
		self.serveur_socket.close()
		closed = True
		GPIO.cleanup()

	def eventLoop(self):
		global closed

		while closed != True:
			if ((int(self.MCP3008.getValue(2)*100/1024)) > 55 and
				self.Motor_L.getSpeed() > 0 and 
				self.Motor_R.getSpeed() > 0 and 
				self.Motor_L.getDirection() == "fw" and
				self.Motor_R.getDirection() == "fw"):

				self.StatusLED.setColor_RGB(100, 0, 255)
				self.StatusLED.blink(0.1)

				self.Motor_L.setSpeed(0)
				self.Motor_R.setSpeed(0)

			time.sleep(0.02)

	# Read loop
	def tcp_read(self):
		while True:
			msg_recu = self.client_socket.recv(1024).decode("utf-8")			
			if msg_recu != "":
				#print(msg_recu)
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

		elif cmd == "eng":
			self.Engine_Module(args)

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
				t = threading.Thread(target = self.FrontLight.flash, args = [args[2]] )
				t.start()
				
			elif args[1] == "status":
				self.tcp_send("fl status {} {}".format(self.FrontLight.isOn(), self.FrontLight.luminosity))

		except: pass

	# --------------------------------------------
	# MODULE STATUS-LED
	# --------------------------------------------
	def StatusLED_Module(self, args):
		try:

			if args[1] == "red":
				self.StatusLED.setColor_RGB(255, 0, 0)
				self.StatusLED.blink(0.5)

			elif args[1] == "green":
				self.StatusLED.setColor_RGB(0, 255, 0)
				self.StatusLED.blink(0.5)

			elif args[1] == "blue":
				self.StatusLED.setColor_RGB(0, 0, 255)
				self.StatusLED.blink(0.5)
				
			elif args[1] == "rgb":
				self.StatusLED.setColor_RGB(int(args[2]), int(args[3]), int(args[4]))
				self.StatusLED.blink(0.5)

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

				self.tcp_send("sns {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(values[0], values[1], values[2], values[3],
					values[4], values[5], values[6], values[7], 256, 256, 256, 256, 256, 256, 256, 256))

		except: pass

	# --------------------------------------------
	# MODULE ENGINE
	# --------------------------------------------
	def Engine_Module(self, args):
		try:
			if args[1] == "fw":
				timer = float(args[2])

				self.Motor_L.setDirection("fw")
				self.Motor_R.setDirection("fw")

				self.Motor_L.setSpeed(100)
				self.Motor_R.setSpeed(100)

				t1 = time.time()

				while (time.time() - t1) <= timer:

					if (int(self.MCP3008.getValue(2)*100/1024)) > 55:
						self.StatusLED.setColor_RGB(100, 0, 255)
						self.StatusLED.blink(0.1)
						break

					time.sleep(0.02)

				self.Motor_L.setSpeed(0)
				self.Motor_R.setSpeed(0)

			elif args[1] == "bw":
				timer = float(args[2])

				self.Motor_L.setDirection("bw")
				self.Motor_R.setDirection("bw")

				self.Motor_L.setSpeed(100)
				self.Motor_R.setSpeed(100)
				time.sleep(timer)
				self.Motor_L.setSpeed(0)
				self.Motor_R.setSpeed(0)

			elif args[1] == "l":
				timer = float(args[2])

				self.Motor_L.setDirection("bw")
				self.Motor_R.setDirection("fw")

				self.Motor_L.setSpeed(100)
				self.Motor_R.setSpeed(100)
				time.sleep(timer)
				self.Motor_L.setSpeed(0)
				self.Motor_R.setSpeed(0)

			elif args[1] == "r":
				timer = float(args[2])

				self.Motor_L.setDirection("fw")
				self.Motor_R.setDirection("bw")

				self.Motor_L.setSpeed(100)
				self.Motor_R.setSpeed(100)
				time.sleep(timer)
				self.Motor_L.setSpeed(0)
				self.Motor_R.setSpeed(0)

			elif args[1] == "forward":
				if (int(self.MCP3008.getValue(2)*100/1024)) < 55:
					self.Motor_L.setDirection("fw")
					self.Motor_R.setDirection("fw")
					self.Motor_L.setSpeed(100)
					self.Motor_R.setSpeed(100)

			elif args[1] == "backward":
				self.Motor_L.setDirection("bw")
				self.Motor_R.setDirection("bw")
				self.Motor_L.setSpeed(100)
				self.Motor_R.setSpeed(100)

			elif args[1] == "left":
				self.Motor_L.setDirection("bw")
				self.Motor_R.setDirection("fw")
				self.Motor_L.setSpeed(100)
				self.Motor_R.setSpeed(100)

			elif args[1] == "right":
				self.Motor_L.setDirection("fw")
				self.Motor_R.setDirection("bw")
				self.Motor_L.setSpeed(100)
				self.Motor_R.setSpeed(100)

			elif args[1] == "stop":
				self.Motor_L.setSpeed(0)
				self.Motor_R.setSpeed(0)

		except: pass


if __name__ == "__main__":
	PyRobot_Serveur = PyRobot_Serveur(12800)
	try:
		PyRobot_Serveur.start()
	except Exception as e:
		print(str(e))
		PyRobot_Serveur.close()