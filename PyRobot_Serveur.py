import socket, sys, subprocess, time, threading, re
import RPi.GPIO as GPIO
import Adafruit_DHT as dht

from FrontLight import FrontLight
from MCP3008_SPI import MCP3008
from LED_RGB import LED_RGB
from Motor_DC import Motor_DC
from MQ_XX import *

closed = True

class PyRobot_Serveur:
	def __init__(self, port):

		self.temperature = 0
		self.humidity = 0

		# Modules (Capteurs , éclairage, etc)
		#self.FrontLight_W = FrontLight(18)        		# PIN : WHITE
		#self.FrontLight_IR = FrontLight(4)						# PIN : IR
		#self.StatusLED = LED_RGB(23, 24, 25)				# PIN : R, G, B

		#MCP3008_1 = MCP3008(12, 16, 20, 21) 	# PIN : CLK, MOSI, MISO, CS
		#MCP3008_2 = MCP3008(6, 13, 19, 26)   	# PIN : CLK, MOSI, MISO, CS

		self.MCP3008_1 = MCP3008(0)
		#MCP3008_2 = MCP3008(1)

		#self.Motor_L = Motor_DC(17, 27, 22) 				# PIN : SPEED, FW, BW
		#self.Motor_R = Motor_DC(10, 9, 11)			  	# PIN : SPEED, FW, BW

		#MQ_2 = MQ_2(MCP3008_2, 1, 10, 9.83)  	# MCP, CHANNEL, RESISTANCE, CLEAN_AIR_FACTOR

		self.hote = ''
		self.port = port

	def setup(self):
		print("Calibrating...")
		#self.MQ_2.MQCalibration()
		print("Calibration done.")
		#self.humidity, self.temperature = dht.read_retry(dht.DHT22, 5)

	# Starting server
	def start(self):
		global closed

		self.serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serveur_socket.bind((self.hote, self.port))
		self.serveur_socket.listen(5)
		self.client_socket = None

		self.setup()
		
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
				if self.client_socket != None:
					self.client_socket.close()
				self.FrontLight_W.off()
				self.FrontLight_IR.off()
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

			if ((int(self.MCP3008_1.getValue(2)*100/1024)) > 55 and
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

		elif cmd == "wifi":
			#stdoutdata = subprocess.getoutput("python3 WifiQuality.py")
			stdoutdata = subprocess.getoutput("iwconfig")
			
			res = re.search(r"(Quality=)([0-9]{0,3})/([0-9]{0,3})", stdoutdata.split()[33])
			if res != None:
				current = int(res.group(2))
				maximum = int(res.group(3))
				percent = int( (current/maximum)*100 )
				#print(percent)

				self.tcp_send("wifi {}".format(percent))

	# --------------------------------------------
	# MODULE FRONT-LIGHTS
	# --------------------------------------------
	def FrontLight_Module(self, args):
		try:
			if args[1] == "w":
				if args[2] == "on":
					self.FrontLight_W.on()

				elif args[2] == "off":
					self.FrontLight_W.off()

				elif args[2] == "flash":
					t = threading.Thread(target = self.FrontLight_W.flash, args = [args[2]] )
					t.start()
					
				elif args[2] == "status":
					self.tcp_send("fl status {}".format(self.FrontLight_W.isOn()))				

			elif args[1] == "ir":

				if args[2] == "on":
					self.FrontLight_W.on()

				elif args[2] == "off":
					self.FrontLight_W.off()

				elif args[2] == "flash":
					t = threading.Thread(target = self.FrontLight_W.flash, args = [args[2]] )
					t.start()
					
				elif args[2] == "status":
					self.tcp_send("fl status {}".format(self.FrontLight_W.isOn()))	


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
					value = self.MCP3008_1.getValue(int(args[1]))
					self.tcp_send("sns "+args[1]+" "+str(value))
					time.sleep(0.5) 

					elapsed = time.time() - start
					if elapsed >= timer:
						break

			else:
				values = [] 
				for e in range(8):
					values += [self.MCP3008_1.getValue(e)]
				for e in range(8):
					#values += [self.MCP3008_2.getValue(e)]
					values += [0]

				self.tcp_send("sns {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(values[0], values[1], values[2], values[3],
					values[4], values[5], values[6], values[7], values[8], values[9], values[10], values[11], values[12], values[13], values[14], values[15], self.temperature, self.humidity))

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

					if (int(self.MCP3008_1.getValue(2)*100/1024)) > 55:
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
				if (int(self.MCP3008_1.getValue(2)*100/1024)) < 55:
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
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)	

	PyRobot_Serveur = PyRobot_Serveur(12800)
	try:
		PyRobot_Serveur.start()
	except Exception as e:
		print(str(e))
		PyRobot_Serveur.close()

	GPIO.cleanup()