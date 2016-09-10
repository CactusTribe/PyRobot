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

				nb_loop = 0
				echantillons = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

				#for e in range(nb_loop):
				while nb_loop < 6:
					self.PyRobot_Client.tcp_send("sns")
					msg_recu = self.PyRobot_Client.tcp_read()
								
					if msg_recu != None: 
						tokens = msg_recu.split(" ")

						if tokens[0] == "sns":

							# LUMINOSITY LEFT
							luminosity_L = int(int(tokens[1])*100/1024)
							# LUMINOSITY RIGHT
							luminosity_R = int(int(tokens[2])*100/1024)
							# DISTANCE
							if int(tokens[3]) > 12:
								distance_L = 2076 / (int(tokens[3]) - 11)
							else:
								distance_L = 0

							distance_R = 0
							# INCLINAISON
							inclinaison = int(int(tokens[5])*100/1024)
							# SOUND
							sound = 100 - (int(int(tokens[6])*100/1024) + 1)

							# TEMP
							#kelvin = Tools.temp_kelvin( ( 3.3 * float( tokens[4] ) ) / 1024 ) - 2

							echantillons[0] += [luminosity_L]
							echantillons[1] += [luminosity_R]
							echantillons[2] += [distance_L]
							echantillons[3] += [distance_R]
							echantillons[4] += [inclinaison]
							echantillons[5] += [sound]
							echantillons[6] += [int(tokens[7])]
							echantillons[7] += [int(tokens[8])]
							echantillons[8] += [int(tokens[9])]
							echantillons[9] += [int(tokens[10])]
							echantillons[10] += [int(tokens[11])]
							echantillons[11] += [int(tokens[12])]
							echantillons[12] += [int(tokens[13])]
							echantillons[13] += [int(tokens[14])]
							echantillons[14] += [int(tokens[15])]
							echantillons[15] += [int(tokens[16])]
							echantillons[16] += [float(tokens[17])]
							echantillons[17] += [float(tokens[18])]

							nb_loop += 1

					time.sleep(0.015)

				for i,e in enumerate(echantillons):
					#if i != 5:
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

		#self.buttonBox.accepted.connect(self.stop_capture)

		self.PyRobot_Client = client

		global capture
		capture = True

		self.Sensors_Capture = Sensors_Capture(self, self.PyRobot_Client)
		self.Sensors_Capture.message_received.connect(self.setValues)
		#self.Sensors_Capture.start()
	

	@pyqtSlot(list)
	def setValues(self, values):
		if len(values) == 18:

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
				self.label_ch3.setStyleSheet("QLabel { font-size:16px; color: rgb(0, 0, 0); }")
				self.progressBar_ch3.setValue(0)
			else:
				self.label_ch3.setStyleSheet("QLabel { font-size:12px; }")
				self.label_ch3.setText("{0:.1f} cm".format(values[2]))
				self.progressBar_ch3.setValue(30 - values[2])

				if values[2] < 7:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
				elif values[2] < 15:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
				else:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			# DISTANCE R
			if values[3] > 35 or values[3] <= 0:
				self.label_ch4.setText("∞")
				self.label_ch4.setStyleSheet("QLabel { font-size:16px; color: rgb(0, 0, 0); }")
				self.progressBar_ch4.setValue(0)
			else:
				self.label_ch4.setStyleSheet("QLabel { font-size:12px; }")
				self.label_ch4.setText("{0:.1f} cm".format(values[3]))
				self.progressBar_ch4.setValue(30 - values[3])

				if values[3] < 7:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
				elif values[3] < 15:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
				else:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			# INCLINAISON
			if values[4] > 50:
				self.label_ch7.setText("100 %")
				self.progressBar_ch7.setValue(1)
				self.label_ch7.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			else:
				self.label_ch7.setText("0 %")
				self.progressBar_ch7.setValue(0)
				self.label_ch7.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			# SOUND
			self.label_ch8.setText("{} %".format(int(values[5])))
			self.progressBar_ch8.setValue(int(values[5]))


			# TEMPERATURE
			self.label_ch5.setText("{:.1f} °C".format(values[16]))
			self.progressBar_ch5.setValue(int(values[16]))

			# HUMIDITY 
			self.label_ch6.setText("{:.1f} %".format(values[17]))
			self.progressBar_ch6.setValue(int(values[17]))



			#=================================
			
			# AIR QUALITY MQ-135
			self.label_ch9.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch9.setText("{} ppm".format(int(values[15])))
			self.progressBar_ch9.setValue(values[15])

			# FLAMMABLE GAS MQ-2
			self.label_ch10.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch10.setText("{} ppm".format(int(values[8])))
			self.progressBar_ch10.setValue(values[8])

			# NATURAL GAS MQ-5
			self.label_ch11.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch11.setText("{} ppm".format(int(values[11])))
			self.progressBar_ch11.setValue(values[11])

			# PETROLEUM GAS MQ-6
			self.label_ch12.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch12.setText("{} ppm".format(int(values[12])))
			self.progressBar_ch12.setValue(values[12])

			# HYDROGEN MQ-8
			self.label_ch13.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch13.setText("{} ppm".format(int(values[14])))
			self.progressBar_ch13.setValue(values[14])

			# CARBON MONOXIDE MQ-7
			self.label_ch14.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch14.setText("{} ppm".format(int(values[13])))
			self.progressBar_ch14.setValue(values[13])

			# METHANE MQ-4
			self.label_ch15.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch15.setText("{} ppm".format(int(values[10])))
			self.progressBar_ch15.setValue(values[10])

			# ETHANOL MQ-3
			self.label_ch16.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")
			self.label_ch16.setText("{} ppm".format(int(values[9])))
			self.progressBar_ch16.setValue(values[9])

			#self.update()
			QApplication.processEvents()

	def stop_capture(self):
		global capture
		capture = False
		self.Sensors_Capture.wait()
		print("Capture stopped")

	def closeEvent(self, event):
		self.stop_capture()
		