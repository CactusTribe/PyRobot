from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc
import socket
from PyRobot_Client import PyRobot_Client

class Dialog_NewConnection(QDialog):

	Main_Client = None
	Event_Client = None
	Sensors_Client = None
	Engine_Client = None
	Camera_Client = None
	IA_Client = None

	def __init__(self):
		QDialog.__init__(self)
		uic.loadUi('interfaces/Dialog_NewConnection.ui', self)

		self.pushButton_sync.clicked.connect(self.startConnection)

	def startConnection(self):
		if self.Main_Client != None:
			self.Main_Client.close()
			self.Event_Client.close()
			self.Sensors_Client.close()
			self.Engine_Client.close()
			self.Camera_Client.close()
			self.IA_Client.close()

		self.Main_Client = PyRobot_Client(self.lineEdit_ip.text(), 12800)
		self.Event_Client = PyRobot_Client(self.lineEdit_ip.text(), 12800)
		self.Sensors_Client = PyRobot_Client(self.lineEdit_ip.text(), 12800)
		self.Engine_Client = PyRobot_Client(self.lineEdit_ip.text(), 12800)
		self.Camera_Client = PyRobot_Client(self.lineEdit_ip.text(), 12800)
		self.IA_Client = PyRobot_Client(self.lineEdit_ip.text(), 12800)

		try:
			self.Main_Client.start()
			self.Event_Client.start()
			self.Sensors_Client.start()
			self.Engine_Client.start()
			self.Camera_Client.start()
			self.IA_Client.start()

			if self.Main_Client.connected == True:
				self.label_status.setText("Connected at {}:{}".format(self.Main_Client.hote, self.Main_Client.port))
			else:
				self.label_status.setText("Connection error.")

				self.Main_Client = None
				self.Event_Client = None
				self.Sensors_Client = None
				self.Engine_Client = None
				self.Camera_Client = None
				self.IA_Client = None

		except ConnectionRefusedError:
			self.Main_Client.close()
			self.label_status.setText("Connection refused.")



