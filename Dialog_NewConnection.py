from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc
import socket
from PyRobot_Client import PyRobot_Client

class Dialog_NewConnection(QDialog):

	PyRobot_Client = None

	def __init__(self):
		QDialog.__init__(self)
		uic.loadUi('Dialog_NewConnection.ui', self)

		self.pushButton_sync.clicked.connect(self.startConnection)

	def startConnection(self):
		if self.PyRobot_Client != None:
			self.PyRobot_Client.close()

		self.PyRobot_Client = PyRobot_Client(self.lineEdit_ip.text(), 12800)

		try:
			self.PyRobot_Client.start()
			if self.PyRobot_Client.connected == True:
				self.label_status.setText("Connected at {}:{}".format(self.PyRobot_Client.hote, self.PyRobot_Client.port))
			else:
				self.label_status.setText("Connection error.")
		except ConnectionRefusedError:
			self.PyRobot_Client.close()
			self.label_status.setText("Connection refused.")



