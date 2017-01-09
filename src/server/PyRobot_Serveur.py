import socket, sys, subprocess, time, threading, re, io, copy
import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import traceback

from devices.Devices import *

from modules.MainModule import MainModule
from modules.EventModule import EventModule
from modules.SensorsModule import SensorsModule
from modules.EngineModule import EngineModule
from modules.CameraModule import CameraModule, camera
from modules.IAModule import IAModule

engine_speed = 100
temperature = 0
humidity = 0
distance_L = 0
distance_R = 0

closed = True

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

		print("Server listening at {}".format(self.port))

	# Starting server
	def start(self):
		global closed

		# INITIALISATION DU SERVEUR
		self.serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serveur_socket.bind((self.hote, self.port))
		self.serveur_socket.listen(5)

		self.clients = {} # Dictionnaire des clients
		self.setup()

		#Threads généraux
		ThreadEvent = threading.Thread(target = self.eventLoop, args = [] )
		SonnarThread = threading.Thread(target = self.Sonnar_Module, args = [])
		ClimatThread = threading.Thread(target = self.Climat_Module, args = [])

		closed = False
		ThreadEvent.start()
		ClimatThread.start()
		#SonnarThread.start()


		#Threads dédiés
		modulesNames = [
			"MainModule", 
			"EventModule", 
			"SensorsModule", 
			"EngineModule", 
			"CameraModule", 
			"IAModule"]

		# Lancement des modules
		i = 0
		while True:
			self.client_socket, self.infos_connexion = self.serveur_socket.accept()

			#Threads clients
			constructor = globals()[modulesNames[i]]
			mod = constructor(modulesNames[i])
			mod.clients = self.clients
			mod.connection = self.client_socket
			mod.start()
			mod.setName(mod.name)
			it = mod.getName()
			self.clients[it] = self.client_socket

			i+=1
			if i == len(modulesNames):
				print(" -> {} is connected.".format(self.client_socket.getsockname()))
				i=0
			
		self.close()
		print("Serveur closed.")


	# Close server
	def close(self):
		global closed
		self.serveur_socket.close()
		closed = True
		FrontLight_W.off()
		FrontLight_IR.off()
		camera.close()
		GPIO.cleanup()

	def eventLoop(self):
		global closed

		while closed != True:

			if MCP3008_1.getValue(4) >= 15:
				dist_IR = (2076 / (MCP3008_1.getValue(4) - 11) )
			else:
				dist_IR = 100

			inclinaison = (MCP3008_1.getValue(3)*100)/1024
			
			if inclinaison > 50:
				if ((dist_IR) > 10 and
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
	def Sonnar_Module(self):
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
		global closed, humidity, temperature

		while closed != True:
			h, t = dht.read_retry(dht.DHT22, DHT22)

			if h == None: h = 0
			if t == None: t = 0

			humidity = copy.copy(h)
			temperature = copy.copy(t)

			time.sleep(2)


if __name__ == "__main__":
	PyRobot_Serveur = PyRobot_Serveur(12800)
	try:
		PyRobot_Serveur.start()
	except KeyboardInterrupt:
		PyRobot_Serveur.close()
	except Exception as e:
		print(e)
		PyRobot_Serveur.close()
	finally:
		GPIO.cleanup()