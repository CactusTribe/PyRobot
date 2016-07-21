from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import resources_rc, threading, time

capture = True

class Dialog_Sensors(QDialog):

	def __init__(self, client):
		QDialog.__init__(self)
		uic.loadUi('Dialog_Sensors.ui', self)

		self.buttonBox.accepted.connect(self.stop_capture)

		self.PyRobot_Client = client
		self.start_capture()

	def setValues(self, values):
		if len(values) == 8:
			self.label_ch1.setText(str(values[0])+" %")
			self.label_ch2.setText(str(values[1])+" %")
			self.label_ch3.setText(str(values[2])+" %")
			self.label_ch4.setText(str(values[3])+" %")
			self.label_ch5.setText(str(values[4])+" %")
			self.label_ch6.setText(str(values[5])+" %")
			self.label_ch7.setText(str(values[6])+" %")
			self.label_ch8.setText(str(values[7])+" %")

	def capture(self):
		while capture == True:
			QApplication.processEvents()

			try:
				self.PyRobot_Client.tcp_send("sns")
				msg_recu = self.PyRobot_Client.tcp_read()
				print(msg_recu)

				if msg_recu != None: 
					tokens = msg_recu.split(" ")

					values = [int(int(tokens[1])*100/1024), 
										int(int(tokens[2])*100/1024), 
										int(int(tokens[3])*100/1024),
										int(int(tokens[4])*100/1024),
										int(int(tokens[5])*100/1024),
										int(int(tokens[6])*100/1024),
										int(int(tokens[7])*100/1024),
										int(int(tokens[8])*100/1024)]

					self.setValues(values)
					self.update()
					time.sleep(0.1)

			except Exception as e:
				print(e)
			

	def start_capture(self):
		global capture
		capture = True
		self.thread_capture = threading.Thread(target=self.capture)
		self.thread_capture.start()

	def stop_capture(self):
		global capture
		capture = False
		print("Capture stopped")
		