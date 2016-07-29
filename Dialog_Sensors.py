from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import resources_rc, threading, time

from Tools import Tools

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

				nb_loop = 10
				values = [0, 0, 0, 0, 0, 0, 0, 0]

				for e in range(nb_loop):

					self.PyRobot_Client.tcp_send("sns")
					msg_recu = self.PyRobot_Client.tcp_read()
					#print(msg_recu)

					if msg_recu != None: 
						tokens = msg_recu.split(" ")

						# TEMP
						kelvin = Tools.temp_kelvin( ( 3.3 * float( tokens[4] ) ) / 1024 ) - 2
						# DISTANCE
						distance = 3080 / (int(tokens[3]) - 17)

						values = [values[0] + int(int(tokens[1])*100/1024), 
											values[1] + int(int(tokens[2])*100/1024),
											values[2] + distance,
											values[3] + kelvin,
											values[4] + int(int(tokens[5])*100/1024),
											values[5] + int(int(tokens[6])*100/1024),
											values[6] + int(int(tokens[7])*100/1024),
											values[7] + int(int(tokens[8])*100/1024)]

					time.sleep(0.02)

				
				values = [elt/nb_loop for elt in values]
				self.message_received.emit(values)
				time.sleep(0.02)
				

			except Exception as e:
				print(e)



class Dialog_Sensors(QDialog):

	Sensors_Capture = None

	def __init__(self, parent, client):
		QDialog.__init__(self, parent)
		uic.loadUi('Dialog_Sensors.ui', self)

		self.buttonBox.accepted.connect(self.stop_capture)

		self.PyRobot_Client = client

		global capture
		capture = True

		self.Sensors_Capture = Sensors_Capture(self, self.PyRobot_Client)
		self.Sensors_Capture.message_received.connect(self.setValues)
		#self.Sensors_Capture.start()
	

	@pyqtSlot(list)
	def setValues(self, values):
		if len(values) == 8:

			# LUMINOSITY LEFT
			if values[0] > 75:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Sun-icon.png"))
			elif values[0] > 50:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Sun2-icon.png"))
			elif values[0] > 25:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Overcast.png"))
			else:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Moon-icon.png"))

			# LUMINOSITY RIGHT
			if values[1] > 75:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Sun-icon.png"))
			elif values[1] > 50:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Sun2-icon.png"))
			elif values[1] > 25:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Overcast.png"))
			else:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Moon-icon.png"))

			self.label_ch1.setText(str(int(values[0]))+" %")
			self.label_ch2.setText(str(int(values[1]))+" %")

			if values[2] > 35 or values[2] < 0:
				self.label_ch3.setText("∞")
			else:
				self.label_ch3.setText("{0:.1f} cm".format(values[2]))

			self.label_ch4.setText("{} °C".format(int(values[3]) - 273))
			self.label_ch5.setText(str(values[4])+" %")
			self.label_ch6.setText(str(values[5])+" %")
			self.label_ch7.setText(str(values[6])+" %")
			self.label_ch8.setText(str(values[7])+" %")

			self.progressBar_ch1.setValue(values[0])
			self.progressBar_ch2.setValue(values[1])

			if values[2] > 30 or values[2] < 0:
				self.progressBar_ch3.setValue(0)
			else:
				self.progressBar_ch3.setValue(30 - values[2])

			self.progressBar_ch4.setValue(int(values[3]))
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
		