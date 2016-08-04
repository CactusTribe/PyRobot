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

				nb_loop = 6
				echantillons = [[], [], [], [], [], [], [], []]

				for e in range(nb_loop):

					self.PyRobot_Client.tcp_send("sns")
					msg_recu = self.PyRobot_Client.tcp_read()
					#print(msg_recu)

					if msg_recu != None: 
						tokens = msg_recu.split(" ")

						# LUMINOSITY LEFT
						luminosity_L = int(int(tokens[1])*100/1024)
						# LUMINOSITY RIGHT
						luminosity_R = int(int(tokens[2])*100/1024)
						# DISTANCE
						distance = 3080 / (int(tokens[3]) - 17)
						# INCLINAISON
						inclinaison = int(int(tokens[8])*100/1024)
						# TEMP
						kelvin = Tools.temp_kelvin( ( 3.3 * float( tokens[4] ) ) / 1024 ) - 2
						# HUMIDITY
						
						echantillons[0] += [luminosity_L]
						echantillons[1] += [luminosity_R]
						echantillons[2] += [distance]
						echantillons[3] += [inclinaison]
						echantillons[4] += [kelvin]
						echantillons[5] += [int(int(tokens[6])*100/1024)]
						echantillons[6] += [int(int(tokens[7])*100/1024)]
						echantillons[7] += [int(int(tokens[8])*100/1024)]

					time.sleep(0.02)

				for e in echantillons:
					e.remove(max(e))
					e.remove(min(e))

				values = [(sum(elt)/len(elt)) for elt in echantillons]
				self.message_received.emit(values)
				#time.sleep(0.05)
				

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
			self.label_ch1.setText(str(int(values[0]))+" %")
			self.progressBar_ch1.setValue(values[0])

			# LUMINOSITY RIGHT
			if values[1] > 75:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Sun-icon.png"))
			elif values[1] > 50:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Sun2-icon.png"))
			elif values[1] > 25:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Overcast.png"))
			else:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Moon-icon.png"))
			self.label_ch2.setText(str(int(values[1]))+" %")
			self.progressBar_ch2.setValue(values[1])

			# DISTANCE L 
			if values[2] > 35 or values[2] <= 0:
				self.label_ch3.setText("∞")
				self.progressBar_ch3.setValue(0)
			else:
				self.label_ch3.setText("{0:.1f} cm".format(values[2]))
				self.progressBar_ch3.setValue(30 - values[2])

				if values[2] < 7:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
				elif values[2] > 7:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
				elif values[2] > 15:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			# DISTANCE R
			if values[6] > 35 or values[6] <= 0:
				self.label_ch4.setText("∞")
				self.label_ch4.setStyleSheet("QLabel { font-size:16px; }")
				self.progressBar_ch4.setValue(0)
			else:
				self.label_ch4.setStyleSheet("QLabel { font-size:12px; }")
				self.label_ch4.setText("{0:.1f} cm".format(values[6]))
				self.progressBar_ch4.setValue(30 - values[6])

				if values[6] < 7:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
				elif values[6] > 7:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
				elif values[6] > 15:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")



			# INCLINAISON
			if values[7] > 50:
				self.label_ch7.setText("100 %")
				self.progressBar_ch7.setValue(1)
				self.label_ch7.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			else:
				self.label_ch7.setText("0 %")
				self.progressBar_ch7.setValue(0)
				self.label_ch7.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			# TEMPERATURE
			self.label_ch5.setText("{} °C".format(int(values[4]) - 273))
			self.progressBar_ch5.setValue(values[4])
			

			# HUMIDITY 
			self.label_ch6.setText("0 %")
			self.progressBar_ch6.setValue(0)

			self.label_ch8.setText("0 dB")
			self.progressBar_ch8.setValue(0)

			#=================================
			
			# AIR QUALITY MQ-135
			self.label_ch9.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch9.setText("0 ppm")
			self.progressBar_ch9.setValue(0)

			# FLAMMABLE GAS MQ-2
			self.label_ch10.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch10.setText("0 ppm")
			self.progressBar_ch10.setValue(0)

			# NATURAL GAS MQ-5
			self.label_ch11.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch11.setText("0 ppm")
			self.progressBar_ch11.setValue(0)

			# PETROLEUM GAS MQ-6
			self.label_ch12.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch12.setText("0 ppm")
			self.progressBar_ch12.setValue(0)

			# HYDROGEN MQ-8
			self.label_ch13.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch13.setText("0 ppm")
			self.progressBar_ch13.setValue(0)

			# CARBON MONOXIDE MQ-7
			self.label_ch14.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch14.setText("0 ppm")
			self.progressBar_ch14.setValue(0)

			# METHANE MQ-4
			self.label_ch15.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch15.setText("0 ppm")
			self.progressBar_ch15.setValue(0)

			# ETHANOL MQ-3
			self.label_ch16.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch16.setText("0 ppm")
			self.progressBar_ch16.setValue(0)

			#self.update()
			QApplication.processEvents()

	def stop_capture(self):
		self.Sensors_Capture.stop()
		self.Sensors_Capture.wait()
		print("Capture stopped")
		