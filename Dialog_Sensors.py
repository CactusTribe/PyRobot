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
				echantillons = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

				while nb_loop < 6:
					self.PyRobot_Client.tcp_send("sns")
					msg_recu = self.PyRobot_Client.tcp_read()
								
					if msg_recu != None: 
						tokens = msg_recu.split(" ")

						if tokens[0] == "sns":

							# MCP3008 1
							luminosity_L = int(int(tokens[1])*100/1024)
							luminosity_R = int(int(tokens[2])*100/1024)
							sound 			 = int(int(tokens[3])*100/768)
							inclinaison  = int(int(tokens[4])*100/1024)
							channel_4    = (2076 / (int(tokens[5]) - 11)) if (int(tokens[5]) > 12) else 0
							channel_5 	 = int(tokens[6])
							channel_6 	 = int(tokens[7])
							channel_7 	 = int(tokens[8])

							# GAZ
							gas_1 = int(tokens[9])
							gas_2 = int(tokens[10])
							gas_3 = float(tokens[11])
							gas_4 = int(tokens[12])
							gas_5 = int(tokens[13])
							gas_6 = int(tokens[14])
							gas_7 = int(tokens[15])
							gas_8 = int(tokens[16])

							# HC-SR04 LEFT
							distance_L = int(tokens[17])
							distance_R = int(tokens[18])

							# TEMPERATURE & HUMIDITY
							temperature = float(tokens[19])
							humidity = float(tokens[20])

							#--------------------------------------------------

							echantillons[0] += [luminosity_L]
							echantillons[1] += [luminosity_R]
							echantillons[2] += [sound]
							echantillons[3] += [inclinaison]
							echantillons[4] += [channel_4]
							echantillons[5] += [channel_5]
							echantillons[6] += [channel_6]
							echantillons[7] += [channel_7]
							echantillons[8] += [gas_1]
							echantillons[9] += [gas_2]
							echantillons[10] += [gas_3]
							echantillons[11] += [gas_4]
							echantillons[12] += [gas_5]
							echantillons[13] += [gas_6]
							echantillons[14] += [gas_7]
							echantillons[15] += [gas_8]
							echantillons[16] += [distance_L]
							echantillons[17] += [distance_R]
							echantillons[18] += [temperature]
							echantillons[19] += [humidity]

							nb_loop += 1

					time.sleep(0.015)

				for i,e in enumerate(echantillons):
					if i != 2:
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
		if len(values) == 20:

			luminosity_L = int(values[0])
			luminosity_R = int(values[1])
			sound 			 = int(values[2])
			inclinaison  = int(values[3])
			distance_IR  = int(values[4])
			channel_5 	 = int(values[5])
			channel_6 	 = int(values[6])
			channel_7 	 = int(values[7])

			gas_1 			 = int(values[8]) if int(values[8]) <= 5000 else 5000
			gas_2 			 = int(values[9])if int(values[9]) <= 5000 else 5000
			gas_3 			 = values[10]
			gas_4 			 = int(values[11]) if int(values[11]) <= 5000 else 5000
			gas_5 			 = int(values[12]) if int(values[12]) <= 5000 else 5000
			gas_6 			 = int(values[13]) if int(values[13]) <= 5000 else 5000
			gas_7 			 = int(values[14]) if int(values[14]) <= 5000 else 5000
			gas_8 			 = int(values[15]) if int(values[15]) <= 5000 else 5000

			distance_L 	 = int(values[16])
			distance_R 	 = int(values[17])

			temperature  = values[18]
			humidity 	 	 = values[19]

			# LUMINOSITY LEFT --------------------------------------------------------------
			if luminosity_L > 75:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Sun-icon.png"))
			elif luminosity_L > 50:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Sun2-icon.png"))
			elif luminosity_L > 25:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Overcast.png"))
			else:
				self.icon_ch1.setPixmap(QPixmap(":/resources/img/resources/img/Moon-icon.png"))

			self.label_ch1.setText(str(luminosity_L)+" %")
			self.progressBar_ch1.setValue(luminosity_L)

			# LUMINOSITY RIGHT --------------------------------------------------------------
			if luminosity_R > 75:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Sun-icon.png"))
			elif luminosity_R > 50:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Sun2-icon.png"))
			elif luminosity_R > 25:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Overcast.png"))
			else:
				self.icon_ch2.setPixmap(QPixmap(":/resources/img/resources/img/Moon-icon.png"))

			self.label_ch2.setText(str(luminosity_R)+" %")
			self.progressBar_ch2.setValue(luminosity_R)

			# SOUND -------------------------------------------------------------------------
			self.label_ch8.setText("{} %".format(sound))
			self.progressBar_ch8.setValue(sound)

			# INCLINAISON -------------------------------------------------------------------
			if inclinaison < 50:
				self.label_ch7.setText("100 %")
				self.progressBar_ch7.setValue(1)
				self.label_ch7.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			else:
				self.label_ch7.setText("0 %")
				self.progressBar_ch7.setValue(0)
				self.label_ch7.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			# DISTANCE IR --------------------------------------------------------------------
			if distance_IR > 35 or distance_IR <= 0:
				self.label_ch3.setText("∞")
				self.label_ch3.setStyleSheet("QLabel { font-size:16px; color: rgb(0, 0, 0); }")
				self.progressBar_ch3.setValue(0)
			else:
				self.label_ch3.setStyleSheet("QLabel { font-size:12px; }")
				self.label_ch3.setText("{} cm".format(distance_IR))
				self.progressBar_ch3.setValue(distance_IR)

				if distance_IR < 7:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
				elif distance_IR < 15:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
				else:
					self.label_ch3.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			# DISTANCE US --------------------------------------------------------------------
			if distance_R > 450 or distance_R <= 0:
				self.label_ch4.setText("∞")
				self.label_ch4.setStyleSheet("QLabel { font-size:16px; color: rgb(0, 0, 0); }")
				self.progressBar_ch4.setValue(0)
			else:
				self.label_ch4.setStyleSheet("QLabel { font-size:12px; }")
				self.label_ch4.setText("{} cm".format(distance_R))
				self.progressBar_ch4.setValue(distance_R)

				if distance_R < 7:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
				elif distance_R < 15:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
				else:
					self.label_ch4.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")


			# TEMPERATURE -------------------------------------------------------------------
			self.label_ch5.setText("{:.1f} °C".format(temperature))
			self.progressBar_ch5.setValue(int(temperature))

			# HUMIDITY ----------------------------------------------------------------------
			self.label_ch6.setText("{:.1f} %".format(humidity))
			self.progressBar_ch6.setValue(int(humidity))

			#=================================
			
			# AIR QUALITY MQ-135
			if gas_1 > 1000:
				self.label_ch9.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_1 > 200:
				self.label_ch9.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch9.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch9.setText("{} ppm".format(gas_1))
			self.progressBar_ch9.setValue(gas_1)

			# FLAMMABLE GAS MQ-2
			if gas_2 > 1000:
				self.label_ch10.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_2 > 200:
				self.label_ch10.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch10.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch10.setText("{} ppm".format(gas_2))
			self.progressBar_ch10.setValue(gas_2)

			# ETHANOL MQ-3
			if gas_3 > 2:
				self.label_ch16.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_3 > 0.8:
				self.label_ch16.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch16.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch16.setText("{:0.2f} mg/L".format(gas_3))
			self.progressBar_ch16.setValue(gas_3)

			# METHANE MQ-4
			if gas_4 > 1000:
				self.label_ch15.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_4 > 200:
				self.label_ch15.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch15.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch15.setText("{} ppm".format(gas_4))
			self.progressBar_ch15.setValue(gas_4)

			# NATURAL GAS MQ-5
			if gas_5 > 1000:
				self.label_ch11.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_5 > 200:
				self.label_ch11.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch11.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch11.setText("{} ppm".format(gas_5))
			self.progressBar_ch11.setValue(gas_5)

			# PETROLEUM GAS MQ-6
			if gas_6 > 1000:
				self.label_ch12.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_6 > 200:
				self.label_ch12.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch12.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch12.setText("{} ppm".format(gas_6))
			self.progressBar_ch12.setValue(gas_6)

			# CARBON MONOXIDE MQ-7
			if gas_7 > 1000:
				self.label_ch14.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_7 > 200:
				self.label_ch14.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch14.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch14.setText("{} ppm".format(gas_7))
			self.progressBar_ch14.setValue(gas_7)

			# HYDROGEN MQ-8
			if gas_8 > 1000:
				self.label_ch13.setStyleSheet("QLabel { color: rgb(255, 0, 0) }")
			elif gas_8 > 200:
				self.label_ch13.setStyleSheet("QLabel { color: rgb(255, 150, 0) }")
			else:
				self.label_ch13.setStyleSheet("QLabel { color: rgb(0, 180, 0) }")

			self.label_ch13.setText("{} ppm".format(gas_8))
			self.progressBar_ch13.setValue(gas_8)

			#self.update()
			QApplication.processEvents()

	def stop_capture(self):
		global capture
		capture = False
		self.Sensors_Capture.wait()
		print("Capture stopped")

	def closeEvent(self, event):
		self.stop_capture()
		