from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc
import socket
from PyRobot_Client import PyRobot_Client

class Dialog_Video(QDialog):

	def __init__(self, parent, client):
		QDialog.__init__(self, parent)
		uic.loadUi('Dialog_Video.ui', self)

		self.capture = False

		self.pushButton_capture.clicked.connect(self.captureState)
		self.pushButton_photo.clicked.connect(self.takePicture)

	def captureState(self):
		if self.capture == False:
			self.capture = True
			buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Pause-icon.png"))
			self.pushButton_capture.setIcon(buttonIcon)

		else:
			self.capture = False
			buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Play-icon.png"))
			self.pushButton_capture.setIcon(buttonIcon)

	def takePicture(self):
		print("Take capture")


	def closeEvent(self, event):
		print("Stop video")

