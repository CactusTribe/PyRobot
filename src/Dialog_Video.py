from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import codecs, base64

import resources_rc
import socket
import struct
import io
import time
from datetime import datetime

from PyRobot_Client import PyRobot_Client
from PIL import Image
from PIL.ImageQt import ImageQt
import cv2
import numpy

capture = True

class Camera_Capture(QThread):
	update_capture = pyqtSignal(io.BytesIO)

	def __init__(self, parent, client):
		super(Camera_Capture, self).__init__(parent)
		self.PyRobot_Client = client
		

	def run(self):
		pipe = self.PyRobot_Client.socket.makefile('rb')

		try:
			while True:
				# Read the length of the image as a 32-bit unsigned int. If the
				# length is zero, quit the loop
				image_len = struct.unpack('<L', pipe.read(struct.calcsize('<L')))[0]
				if not image_len:
				  break

				# Construct a stream to hold the image data and read the image
				# data from the connection
				image_stream = io.BytesIO()
				image_stream.write(pipe.read(image_len))
				# Rewind the stream, open it as an image with PIL and do some
				# processing on it
				image_stream.seek(0)
				self.update_capture.emit(image_stream)

			pipe.close()

		except Exception as e:
			print(e)
			pipe.close()


class Dialog_Video(QDialog):
	Camera_Thread = None
	last_image = None

	def __init__(self, parent, client):
		QDialog.__init__(self, parent)
		uic.loadUi('interfaces/Dialog_Video.ui', self)
		self.PyRobot_Client = client

		self.pushButton_capture.clicked.connect(self.captureState)
		self.pushButton_photo.clicked.connect(self.takePicture)

		self.beer_cascade = cv2.CascadeClassifier("beer_cascade_1.xml")

	def captureState(self):
		global capture
		if capture == False:
			self.startCapture()
		else:
			self.stopCapture()

	def pil2qpixmap(self, pil_image):
		try:
			imageq = ImageQt(pil_image)
			qimage = QImage(imageq)
			qimage = qimage.scaled(self.label_camera.width(),self.label_camera.height());
			pix = QPixmap.fromImage(qimage)
			return pix
		except Exception as e:
			print(e)

	def takePicture(self):
		print("Take picture")
		self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_orange.png"))

		if self.last_image != None:
			self.last_image.save("camera_pictures/screen_{}.jpg".format(datetime.now().strftime("%H-%M-%S_%d:%m:%y")))

			global capture
			if capture == True:
				self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_blue.png"))
			else:
				self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_off.png"))


	@pyqtSlot(io.BytesIO)
	def update_view(self, img):
		try:
			image = Image.open(img)
			self.last_image = image
			self.pix = self.pil2qpixmap(image)
			
			"""
			# TEST OBJECT RECOGNITION
			opencvImage = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
			gray = cv2.cvtColor(opencvImage, cv2.COLOR_BGR2GRAY)
			objects = self.beer_cascade.detectMultiScale(gray, 20, 20)

			for (x,y,w,h) in objects:
				cv2.rectangle(opencvImage,(x,y),(x+w,y+h),(255,255,0),2)

			image_modif = QImage(opencvImage, opencvImage.shape[1], opencvImage.shape[0], opencvImage.shape[1] * 3, QImage.Format_RGB888)
			pix_modif = QPixmap(image_modif)
			#self.label_camera.setPixmap(pix_modif)
			# ------------------------------
			"""

			self.label_camera.setPixmap(self.pix)

		except Exception as e:
			print(e)


	def startCapture(self):
		global capture
		capture = True
		self.PyRobot_Client.tcp_send("cam start")

		self.Camera_Thread = Camera_Capture(self, self.PyRobot_Client)
		self.Camera_Thread.update_capture.connect(self.update_view)
		self.Camera_Thread.start()

		print("Capture started !")
		buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Pause-icon.png"))
		self.pushButton_capture.setIcon(buttonIcon)
		self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_blue.png"))

	def stopCapture(self):
		global capture
		capture = False
		self.PyRobot_Client.tcp_send("cam stop")

		if self.Camera_Thread != None:
			self.Camera_Thread.wait()
			self.Camera_Thread = None

		print("Capture stoped !")
		buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Play-icon.png"))
		self.pushButton_capture.setIcon(buttonIcon)
		self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_off.png"))


	def closeEvent(self, event):
		global capture
		if capture == True:
			self.stopCapture()

