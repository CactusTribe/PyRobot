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

from PyRobot_Client import PyRobot_Client
from PIL import Image
from PIL.ImageQt import ImageQt

class Camera_Capture(QThread):
	update_capture = pyqtSignal(io.BytesIO)

	capture = True

	def __init__(self, parent, client):
		super(Camera_Capture, self).__init__(parent)
		self.PyRobot_Client = client

	def run(self):
		self.PyRobot_Client.tcp_send("cam start")
		connection = self.PyRobot_Client.socket.makefile('rb')

		# Read the length of the image as a 32-bit unsigned int. If the
		# length is zero, quit the loop
		while self.capture:
			image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
			if not image_len:
			  break

			# Construct a stream to hold the image data and read the image
			# data from the connection
			image_stream = io.BytesIO()
			image_stream.write(connection.read(image_len))
			# Rewind the stream, open it as an image with PIL and do some
			# processing on it
			image_stream.seek(0)
			self.update_capture.emit(image_stream)



class Dialog_Video(QDialog):
	Camera_Thread = None

	def __init__(self, parent, client):
		QDialog.__init__(self, parent)
		uic.loadUi('Dialog_Video.ui', self)
		self.PyRobot_Client = client

		#self.Camera_Thread = Camera_Capture(self, self.PyRobot_Client)
		#self.Camera_Thread.update_capture.connect(self.update_view)

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
			self.startCapture()

		else:
			self.capture = False
			buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Play-icon.png"))
			self.pushButton_capture.setIcon(buttonIcon)
			self.stopCapture()

			

	def pil2qpixmap(self, pil_image):
		imageq = ImageQt(pil_image)
		qimage = QImage(imageq)
		pix = QPixmap.fromImage(qimage)
		return pix

	def takePicture(self):
		print("Take picture")


	@pyqtSlot(io.BytesIO)
	def update_view(self, img):
		try:
			image = Image.open(img)
			#print('Image is %dx%d' % image.size)

			self.pix = self.pil2qpixmap(image)
			self.label_camera.setPixmap(self.pix)
		except Exception as e:
			print(e)


	def startCapture(self):
		self.threadParent = QObject()
		self.Camera_Thread = Camera_Capture(self.threadParent, self.PyRobot_Client)
		self.Camera_Thread.update_capture.connect(self.update_view)
		self.Camera_Thread.start()
		print("Capture started !")

	def stopCapture(self):
		if self.Camera_Thread != None:
			self.Camera_Thread.capture = False
		print("Capture stoped !")

	def closeEvent(self, event):
		self.stopCapture()

