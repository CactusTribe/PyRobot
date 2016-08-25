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

	def exportAsPng(self, fileName):
		pixmap = QImage(self.graphicsView.width(), self.graphicsView.height(), QImage.Format_ARGB32_Premultiplied)
		 
		painter = QPainter()
		painter.begin(pixmap)
		painter.setRenderHint(QPainter.Antialiasing, True)
		self.graphicsView.render(painter)
		painter.end()
		 
		pixmap.save(fileName, "PNG")

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
		self.exportAsPng("screen0.png")


	def closeEvent(self, event):
		print("Stop video")

