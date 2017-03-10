from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import codecs, base64
import traceback

import resources_rc
import socket
import struct
import io
import time
import os
from datetime import datetime
import subprocess as sp

from PyRobot_Client import PyRobot_Client
from PIL import Image
from PIL.ImageQt import ImageQt
import cv2
import numpy
import copy

capture = False
recording = False

class Camera_Capture(QThread):
	update_capture = pyqtSignal(io.BytesIO)

	def __init__(self, parent, client):
		super(Camera_Capture, self).__init__(parent)
		self.PyRobot_Client = client

	def run(self):
		pipe = self.PyRobot_Client.socket.makefile('rb')
		out = None
		i = 0

		if recording == True:
			print("Create video file")
			command = [ "ffmpeg",
				'-y', # (optional) overwrite output file if it exists
				'-f', 'rawvideo',
				'-vcodec','rawvideo',
				'-s', '480x320', # size of one frame
				'-pix_fmt', 'rgb24',
				'-r', '10', # frames per second
				'-i', '-', # The imput comes from a pipe
				'-an', # Tells FFMPEG not to expect any audio
				'-vcodec', 'mpeg4',
				'camera_videos/video_{}.mp4'.format(datetime.now().strftime("%H-%M-%S_%d-%m-%y"))]

			out = sp.Popen(command, stdin=sp.PIPE, stderr=None)

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
				i += 1
				# Rewind the stream, open it as an image with PIL and do some
				# processing on it
				image_stream.seek(0)

				if out != None:
					image = Image.open(copy.copy(image_stream))
					array = numpy.array(image)
					out.stdin.write(array.tostring())

				self.update_capture.emit(copy.copy(image_stream))

			if out != None:
				print(" <*> Close file")
				out.stdin.close()
				out.wait()
				del out

			pipe.close()

			print(" (*) " + str(i) + " frames received")

		except Exception as e:
			if out != None:
				print(out.stderr.read())
			print(e)
			traceback.print_exc()
			pipe.close()


class Frame_Camera(QFrame):
	Camera_Thread = None
	last_image = None

	def __init__(self, parent, client):
		QDialog.__init__(self, parent)
		if(os.uname()[0] == "Darwin"):
			uic.loadUi('interfaces_osx/Frame_Camera.ui', self)
		else:
			uic.loadUi('interfaces_linux/Frame_Camera.ui', self)

		self.PyRobot_Client = client

		self.pushButton_capture.clicked.connect(self.captureState)
		self.pushButton_recording.clicked.connect(self.recordingState)
		self.pushButton_photo.clicked.connect(self.takePicture)

		self.beer_cascade = cv2.CascadeClassifier("beer_cascade_1.xml")

	def setClient(self, client):
		self.PyRobot_Client = client

	def captureState(self):
		global capture
		if capture == False:
			self.startCapture()
		else:
			self.stopCapture()

	def recordingState(self):
		global recording
		if recording == False:
			recording = True
			self.startCapture()
		else:
			recording = False
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
			self.last_image.save("camera_pictures/screen_{}.jpg".format(datetime.now().strftime("%H-%M-%S_%d-%m-%y")))
			#self.last_image.save("{}/camera_pictures/screen_{}.jpg".format("../../..",datetime.now().strftime("%H-%M-%S_%d-%m-%y")))

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
			objects = self.beer_cascade.detectMultiScale(gray, 200, 200)

			for (x,y,w,h) in objects:
				cv2.rectangle(opencvImage,(x,y),(x+w,y+h),(255,255,0),2)

			image_modif = QImage(opencvImage, opencvImage.shape[1], opencvImage.shape[0], opencvImage.shape[1] * 3, QImage.Format_RGB888)
			pix_modif = QPixmap(image_modif)
			self.label_camera.setPixmap(pix_modif)
			# ------------------------------
			"""

			self.label_camera.setPixmap(self.pix)

		except Exception as e:
			print(e)
			traceback.print_exc()


	def startCapture(self):
		global capture, recording
		capture = True
		self.PyRobot_Client.tcp_send("cam start")

		self.Camera_Thread = Camera_Capture(self, self.PyRobot_Client)
		self.Camera_Thread.update_capture.connect(self.update_view)
		self.Camera_Thread.start()

		if recording == False:
			print("Capture started !")
			buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Actions-media-playback-pause-icon.png"))
			self.pushButton_capture.setIcon(buttonIcon)
			self.pushButton_capture.setEnabled(True)
			self.pushButton_recording.setEnabled(False)
			self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_blue.png"))
		else:
			print("Recording started !")
			buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Actions-media-playback-stop-icon.png"))
			self.pushButton_recording.setIcon(buttonIcon)
			self.pushButton_capture.setEnabled(False)
			self.pushButton_recording.setEnabled(True)
			self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_red.png"))

	def stopCapture(self):
		global capture, recording
		capture = False
		self.PyRobot_Client.tcp_send("cam stop")

		if self.Camera_Thread != None:
			self.Camera_Thread.wait()
			self.Camera_Thread = None

		print("Capture stoped !")
		buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Actions-media-playback-start-icon.png"))
		self.pushButton_capture.setIcon(buttonIcon)
		buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Actions-media-record-icon.png"))
		self.pushButton_recording.setIcon(buttonIcon)
		self.label_captureStatut.setPixmap(QPixmap(":/resources/img/resources/img/round_button_off.png"))

		self.pushButton_capture.setEnabled(True)
		self.pushButton_recording.setEnabled(True)


	def closeEvent(self, event):
		global capture
		if capture == True:
			self.stopCapture()

