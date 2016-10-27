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

capture = True

class Camera_Capture(QThread):
	update_capture = pyqtSignal(io.BytesIO)

	def __init__(self, parent, client):
		super(Camera_Capture, self).__init__(parent)
		self.PyRobot_Client = client
		self.connection = self.PyRobot_Client.socket.makefile('rb')
		#self.capture = True

	def stop(self):
		global capture
		capture = False

	def run(self):
		self.PyRobot_Client.tcp_send("cam start")

		try:
			global capture

			while capture != False:
				# Read the length of the image as a 32-bit unsigned int. If the
				# length is zero, quit the loop
				image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
				if not image_len:
				  break

				# Construct a stream to hold the image data and read the image
				# data from the connection
				image_stream = io.BytesIO()
				image_stream.write(self.connection.read(image_len))
				# Rewind the stream, open it as an image with PIL and do some
				# processing on it
				image_stream.seek(0)
				self.update_capture.emit(image_stream)

		except Exception as e:
			print(e)
			capture = False
			self.connection.close()
		finally:
			capture = False
			self.connection.close()


class Dialog_Video(QDialog):
	Camera_Thread = None
	last_image = None

	def __init__(self, parent, client):
		QDialog.__init__(self, parent)
		uic.loadUi('interfaces/Dialog_Video.ui', self)
		self.PyRobot_Client = client

		global capture
		capture = True

		self.Camera_Thread = Camera_Capture(self, self.PyRobot_Client)
		self.Camera_Thread.update_capture.connect(self.update_view)

		self.pushButton_capture.clicked.connect(self.captureState)
		self.pushButton_photo.clicked.connect(self.takePicture)


	def captureState(self):
		if self.Camera_Thread == None:
			self.startCapture()
		else:
			self.stopCapture()

	def pil2qpixmap(self, pil_image):
		imageq = ImageQt(pil_image)
		qimage = QImage(imageq)
		qimage = qimage.scaled(self.label_camera.width(),self.label_camera.height());
		pix = QPixmap.fromImage(qimage)
		return pix

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
			self.label_camera.setPixmap(self.pix)
		except Exception as e:
			print(e)


	def startCapture(self):
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

		if self.Camera_Thread != None:
			self.Camera_Thread.stop()
			self.Camera_Thread.wait()
			self.Camera_Thread = None

		print("Capture stoped !")
		buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Play-icon.png"))
		self.pushButton_capture.setIcon(buttonIcon)
		self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_off.png"))

	def closeEvent(self, event):
		self.stopCapture()

