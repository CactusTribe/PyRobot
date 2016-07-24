from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import resources_rc, threading, time

capture = True

class Sensors_Capture(QThread):
	message_received = pyqtSignal(list)

	def __init__(self, parent, client):
		super(Sensors_Capture, self).__init__(parent)
		self.PyRobot_Client = client

	def stop(self):
		global capture
		capture = False

	def run(self):
		global capture
		while capture != False:
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


					self.message_received.emit(values)
					time.sleep(0.1)

			except Exception as e:
				print(e)



class Dialog_Sensors(QDialog):

	Sensors_Capture = None

	def __init__(self, client):
		QDialog.__init__(self)
		uic.loadUi('Dialog_Sensors.ui', self)

		self.buttonBox.accepted.connect(self.stop_capture)

		self.PyRobot_Client = client

		global capture
		capture = True

		self.Sensors_Capture = Sensors_Capture(self, self.PyRobot_Client)
		self.Sensors_Capture.message_received.connect(self.setValues)
		self.Sensors_Capture.start()
	

	@pyqtSlot(list)
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

			self.progressBar_ch1.setValue(values[0])
			self.progressBar_ch2.setValue(values[1])
			self.progressBar_ch3.setValue(values[2])
			self.progressBar_ch4.setValue(values[3])
			self.progressBar_ch5.setValue(values[4])
			self.progressBar_ch6.setValue(values[5])
			self.progressBar_ch7.setValue(values[6])
			self.progressBar_ch8.setValue(values[7])

			#self.update()
			QApplication.processEvents()

	def stop_capture(self):
		self.Sensors_Capture.stop()
		self.Sensors_Capture.wait()
		print("Capture stopped")
		