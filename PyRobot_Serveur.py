import socket, sys, subprocess, time, threading, re
import RPi.GPIO as GPIO
import Adafruit_DHT as dht

from FrontLight import FrontLight
from MCP3008_SPI import MCP3008
from LED_RGB import LED_RGB
from Motor_DC import Motor_DC
from MQ_XX import *
from HC_SR04 import HC_SR04

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)	

temperature = 0
humidity = 0
distance_L = 0
distance_R = 0

# Modules (Capteurs , éclairage, etc)
FrontLight_W = FrontLight(18)        		# PIN : WHITE
FrontLight_IR = FrontLight(23)					# PIN : IR
StatusLED = LED_RGB(17, 27, 22)				  # PIN : R, G, B

HC_SR04_L = HC_SR04(19, 26) 						# PIN : TRIGGER, ECHO
HC_SR04_R = HC_SR04(6, 13) 							# PIN : TRIGGER, ECHO
DHT22 = 5																# PIN : AOUT

Motor_L = Motor_DC(21, 20, 16) 					# PIN : SPEED, FW, BW
Motor_R = Motor_DC(12, 25, 24)			  	# PIN : SPEED, FW, BW

MCP3008_1 = MCP3008(0)									# SPI device number
MCP3008_2 = MCP3008(1)									# SPI device number

MQ_2 = MQ_2(MCP3008_2, 0, 9.83)  				# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_3 = MQ_3(MCP3008_2, 1, 60)  					# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_4 = MQ_4(MCP3008_2, 2, 1)  					# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_5 = MQ_5(MCP3008_2, 3, 6.5)  				# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_6 = MQ_6(MCP3008_2, 4, 10)  	  			# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_7 = MQ_7(MCP3008_2, 5, 28)  	  			# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_8 = MQ_8(MCP3008_2, 6, 1)  	  			# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_135 = MQ_135(MCP3008_2, 7, 3.6) 			# MCP, CHANNEL, CLEAN_AIR_FACTOR

closed = True

class ThreadClient(threading.Thread):
	def __init__(self, conn, clients):
		threading.Thread.__init__(self)
		self.connection = conn
		self.clients = clients

	def run(self):
		nom = self.getName()

		while True:
			msg_recu = self.connection.recv(1024).decode("utf-8")			
			if msg_recu != "":
				self.execute_cmd(msg_recu)
			else: break

		self.connection.close()
		del self.clients[nom]
		print("Client {} déconnecté.".format(nom))

	# Send message to client
	def tcp_send(self, msg):
		self.connection.send(bytes(msg, 'utf-8'))

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

				self.tcp_send("wifi {}".format(percent))

	# --------------------------------------------
	# MODULE FRONT-LIGHTS
	# --------------------------------------------
	def FrontLight_Module(self, args):
		try:
			if args[1] == "w":
				if args[2] == "on":
					FrontLight_W.on()

				elif args[2] == "off":
					FrontLight_W.off()

				elif args[2] == "flash":
					t = threading.Thread(target = FrontLight_W.flash, args = [args[2]] )
					t.start()
					
				elif args[2] == "status":
					self.tcp_send("fl status {}".format(FrontLight_W.isOn()))				

			elif args[1] == "ir":

				if args[2] == "on":
					FrontLight_IR.on()

				elif args[2] == "off":
					FrontLight_IR.off()

				elif args[2] == "flash":
					t = threading.Thread(target = FrontLight_IR.flash, args = [args[2]] )
					t.start()
					
				elif args[2] == "status":
					self.tcp_send("fl status {}".format(FrontLight_IR.isOn()))	


		except: pass

	# --------------------------------------------
	# MODULE STATUS-LED
	# --------------------------------------------
	def StatusLED_Module(self, args):
		try:

			if args[1] == "red":
				StatusLED.setColor_RGB(255, 0, 0)
				StatusLED.blink(0.5)

			elif args[1] == "green":
				StatusLED.setColor_RGB(0, 255, 0)
				StatusLED.blink(0.5)

			elif args[1] == "blue":
				StatusLED.setColor_RGB(0, 0, 255)
				StatusLED.blink(0.5)
				
			elif args[1] == "rgb":
				StatusLED.setColor_RGB(int(args[2]), int(args[3]), int(args[4]))
				StatusLED.blink(0.5)

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
					value = MCP3008_1.getValue(int(args[1]))
					self.tcp_send("sns "+args[1]+" "+str(value))
					time.sleep(0.5) 

					elapsed = time.time() - start
					if elapsed >= timer:
						break

			else:
				values = [] 
				for e in range(8):
					values += [MCP3008_1.getValue(e)]

				luminosity_R = values[0]
				luminosity_L = values[1]
				sound 			 = values[2]
				inclinaison  = values[3]
				channel_4    = values[4]
				channel_5 	 = values[5]
				channel_6 	 = values[6]
				channel_7 	 = values[7]

				gas_1 			 = int(MQ_135.MQGetGasPercentage("GAS_CH3_2CO"))
				gas_2 			 = int(MQ_2.MQGetGasPercentage("GAS_SMOKE"))
				gas_3 			 = str(MQ_3.MQGetGasPercentage("GAS_ALCOHOL"))[:5]
				gas_4 			 = int(MQ_4.MQGetGasPercentage("GAS_CH4"))
				gas_5 			 = int(MQ_5.MQGetGasPercentage("GAS_CH4"))
				gas_6 			 = int(MQ_6.MQGetGasPercentage("GAS_LPG"))
				gas_7 			 = int(MQ_7.MQGetGasPercentage("GAS_CO"))
				gas_8 			 = int(MQ_8.MQGetGasPercentage("GAS_H2"))

				dist_L 	 = int(distance_L)
				dist_R 	 = int(distance_R)

				self.tcp_send("sns {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(
					luminosity_L, luminosity_R, sound, inclinaison, channel_4, channel_5, channel_6, channel_7, 
					gas_1, gas_2, gas_3, gas_4, gas_5, gas_6, gas_7, gas_8,
					dist_L, dist_R, temperature, humidity ))
					
		except Exception as e:
			print(e)
			self.tcp_send("sns 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0")

	# --------------------------------------------
	# MODULE ENGINE
	# --------------------------------------------
	def Engine_Module(self, args):
		try:
			if args[1] == "fw":
				timer = float(args[2])

				Motor_L.setDirection("fw")
				Motor_R.setDirection("fw")

				Motor_L.setSpeed(100)
				Motor_R.setSpeed(100)

				t1 = time.time()

				while (time.time() - t1) <= timer:

					if (int(MCP3008_1.getValue(2)*100/1024)) > 55:
						StatusLED.setColor_RGB(100, 0, 255)
						StatusLED.blink(0.1)
						break

					time.sleep(0.02)

				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "bw":
				timer = float(args[2])

				Motor_L.setDirection("bw")
				Motor_R.setDirection("bw")

				Motor_L.setSpeed(100)
				Motor_R.setSpeed(100)
				time.sleep(timer)
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "l":
				timer = float(args[2])

				Motor_L.setDirection("bw")
				Motor_R.setDirection("fw")

				Motor_L.setSpeed(100)
				Motor_R.setSpeed(100)
				time.sleep(timer)
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "r":
				timer = float(args[2])

				Motor_L.setDirection("fw")
				Motor_R.setDirection("bw")

				Motor_L.setSpeed(100)
				Motor_R.setSpeed(100)
				time.sleep(timer)
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "forward":
				if (int(MCP3008_1.getValue(2)*100/1024)) < 55:
					Motor_L.setDirection("fw")
					Motor_R.setDirection("fw")
					Motor_L.setSpeed(100)
					Motor_R.setSpeed(100)

			elif args[1] == "backward":
				Motor_L.setDirection("bw")
				Motor_R.setDirection("bw")
				Motor_L.setSpeed(100)
				Motor_R.setSpeed(100)

			elif args[1] == "left":
				Motor_L.setDirection("bw")
				Motor_R.setDirection("fw")
				Motor_L.setSpeed(100)
				Motor_R.setSpeed(100)

			elif args[1] == "right":
				Motor_L.setDirection("fw")
				Motor_R.setDirection("bw")
				Motor_L.setSpeed(100)
				Motor_R.setSpeed(100)

			elif args[1] == "stop":
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

		except: pass



class PyRobot_Serveur:
	def __init__(self, port):
		self.hote = ''
		self.port = port

	def setup(self):
		print("Calibrating...")
		print(" -> MQ-2")
		MQ_2.MQCalibration()
		print(" -> MQ-3")
		MQ_3.MQCalibration()
		print(" -> MQ-4")
		MQ_4.MQCalibration()
		print(" -> MQ-5")
		MQ_5.MQCalibration()
		print(" -> MQ-6")
		MQ_6.MQCalibration()
		print(" -> MQ-7")
		MQ_7.MQCalibration()
		print(" -> MQ-8")
		MQ_8.MQCalibration()
		print(" -> MQ-135")
		MQ_135.MQCalibration()
		print("Calibration done.")

	# Starting server
	def start(self):
		global closed

		# INITIALISATION DU SERVEUR
		self.serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serveur_socket.bind((self.hote, self.port))
		self.serveur_socket.listen(5)

		self.clients = {} # Dictionnaire des clients

		self.setup()
		
		while True:
			print("Server listening at {}".format(self.port))

			self.client_socket, self.infos_connexion = self.serveur_socket.accept()
			closed = False

			#Threads clients
			th = ThreadClient(self.client_socket, self.clients)
			th.start()
			it = th.getName()
			self.clients[it] = self.client_socket
			print("Client connected with IP {} PORT {}".format(self.infos_connexion[0], self.infos_connexion[1]))


			#Threads généraux
			ThreadEvent = threading.Thread(target = self.eventLoop, args = [] )
			DistanceThread = threading.Thread(target = self.Distance_Module, args = [])
			ClimatThread = threading.Thread(target = self.Climat_Module, args = [])

			#ThreadEvent.start()
			#DistanceThread.start()
			#ClimatThread.start()

		self.close()
		print("Serveur closed.")


	# Close server
	def close(self):
		global closed
		self.serveur_socket.close()
		closed = True
		FrontLight_W.off()
		FrontLight_IR.off()
		GPIO.cleanup()

	def eventLoop(self):
		global closed

		while closed != True:

			if ((int(MCP3008_1.getValue(2)*100/1024)) > 55 and
				Motor_L.getSpeed() > 0 and 
				Motor_R.getSpeed() > 0 and 
				Motor_L.getDirection() == "fw" and
				Motor_R.getDirection() == "fw"):

				StatusLED.setColor_RGB(100, 0, 255)
				StatusLED.blink(0.1)

				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			time.sleep(0.02)


	# --------------------------------------------
	# MODULE DISTANCE
	# --------------------------------------------
	def Distance_Module(self):
		global closed

		while closed != True:
			distance_L = HC_SR04_L.getDistance()
			distance_R = HC_SR04_R.getDistance()
			time.sleep(0.02)

		"""
			NB_LOOP = 4
			echantillons = [[],[]]

			for i in range(NB_LOOP):
				distance_L = HC_SR04_L.getDistance()
				distance_R = HC_SR04_R.getDistance()
				echantillons[0] += [distance_L]
				echantillons[1] += [distance_R]
				time.sleep(0.02)

			echantillons[0].remove(max(echantillons[0]))
			echantillons[0].remove(min(echantillons[0]))

			echantillons[1].remove(max(echantillons[1]))
			echantillons[1].remove(min(echantillons[1]))

			distance_L = sum(echantillons[0]) / len(echantillons[0])
			distance_R = sum(echantillons[1]) / len(echantillons[1])

		"""

	# --------------------------------------------
	# MODULE CLIMAT
	# --------------------------------------------
	def Climat_Module(self):
		global closed

		while closed != True:
			humidity, temperature = dht.read_retry(dht.DHT22, DHT22)

			if humidity == None: humidity = 0
			if temperature == None: temperature = 0

			time.sleep(2)




if __name__ == "__main__":

	PyRobot_Serveur = PyRobot_Serveur(12800)
	try:
		PyRobot_Serveur.start()
	except Exception as e:
		print(str(e))
		PyRobot_Serveur.close()

	GPIO.cleanup()