from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc
import io
import time
import os

from PyRobot_Client import PyRobot_Client
from CurvePaintWidget import CurvePaintWidget

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
				values = []
				self.PyRobot_Client.tcp_send("sns")
				msg_recu = self.PyRobot_Client.tcp_read()
							
				if msg_recu != None: 
					tokens = msg_recu.split(" ")
					if tokens[0] == "sns":

						temperature = float(tokens[19])
						humidity = float(tokens[20])
						distance_IR = (2076 / (int(tokens[5]) - 11)) if (int(tokens[5]) > 12) else 0
						distance_SN = int(tokens[18])

						values += [temperature]
						values += [humidity]
						values += [distance_IR]
						values += [distance_SN]

				self.message_received.emit(values)
				time.sleep(0.05)

			except Exception as e:
				print(e)

class Frame_SensorsCurves(QFrame):

	def __init__(self, parent, client):
		QDialog.__init__(self, parent)
		if(os.uname()[0] == "Darwin"):
			uic.loadUi('interfaces_osx/Frame_SensorsCurves.ui', self)
		else:
			uic.loadUi('interfaces_linux/Frame_SensorsCurves.ui', self)
				
		self.PyRobot_Client = client

		global capture
		capture = True

		self.showCurveId = 0

		self.Sensors_Capture = Sensors_Capture(self, self.PyRobot_Client)
		self.Sensors_Capture.message_received.connect(self.setValues)

		self.pushButton_temperature.clicked.connect(self.showTempCurve)
		self.pushButton_humidity.clicked.connect(self.showHumidityCurve)
		self.pushButton_ir.clicked.connect(self.showIRCurve)
		self.pushButton_sn.clicked.connect(self.showSNCurve)
		
		temperature_colors = {
			(-278, 1000):QColor(255,0,0),
			(-20, 60):QColor(255,180,0),
			(0, 30):QColor(0,180,0)}

		humidity_colors = {
			(40, 60):QColor(0,180,0),
			(20, 70):QColor(255,180,0),
			(0, 100):QColor(255,0,0)}

		distance_ir_colors = {
			(0, 35):QColor(255,0,0),
			(0, 18):QColor(255,180,0),
			(0, 7):QColor(0,180,0)}

		distance_sn_colors = {
			(0, 450):QColor(0,180,0),
			(0, 15):QColor(255,180,0),
			(0, 7):QColor(255,0,0)}

		self.temp_curve = CurvePaintWidget()
		self.temp_curve.setUnit("°C")
		self.temp_curve.setPasX(2)
		self.temp_curve.addColorSet(temperature_colors)
		self.temp_curve.setMinimum(-50)
		self.temp_curve.setMaximum(100)

		self.humidity_curve = CurvePaintWidget()
		self.humidity_curve.setUnit("%")
		self.humidity_curve.setPasX(2)
		self.humidity_curve.addColorSet(humidity_colors)
		self.humidity_curve.setMinimum(0)
		self.humidity_curve.setMaximum(100)
		self.humidity_curve.hide()

		self.distance_ir_curve = CurvePaintWidget()
		self.distance_ir_curve.setUnit("cm")
		self.distance_ir_curve.setPasX(2)
		self.distance_ir_curve.addColorSet(distance_ir_colors)
		self.distance_ir_curve.setMinimum(0)
		self.distance_ir_curve.setMaximum(40)
		self.distance_ir_curve.hide()

		self.distance_sn_curve = CurvePaintWidget()
		self.distance_sn_curve.setUnit("cm")
		self.distance_sn_curve.setPasX(2)
		self.distance_sn_curve.addColorSet(distance_sn_colors)
		self.distance_sn_curve.setMinimum(0)
		self.distance_sn_curve.setMaximum(200)
		self.distance_sn_curve.hide()

		self.horizontalLayout.addWidget(self.temp_curve)
		self.horizontalLayout.addWidget(self.humidity_curve)
		self.horizontalLayout.addWidget(self.distance_ir_curve)
		self.horizontalLayout.addWidget(self.distance_sn_curve)


	def showTempCurve(self):
		self.temp_curve.show()
		self.humidity_curve.hide()
		self.distance_ir_curve.hide()
		self.distance_sn_curve.hide()
		self.showCurveId = 0

	def showHumidityCurve(self):
		self.temp_curve.hide()
		self.humidity_curve.show()
		self.distance_ir_curve.hide()
		self.distance_sn_curve.hide()
		self.showCurveId = 1

	def showIRCurve(self):
		self.temp_curve.hide()
		self.humidity_curve.hide()
		self.distance_ir_curve.show()
		self.distance_sn_curve.hide()
		self.showCurveId = 2

	def showSNCurve(self):
		self.temp_curve.hide()
		self.humidity_curve.hide()
		self.distance_ir_curve.hide()
		self.distance_sn_curve.show()
		self.showCurveId = 3

	@pyqtSlot(list)
	def setValues(self, values):
		if len(values) >= 4:
			temperature = values[0]
			humidity = values[1]
			distance_IR = values[2]
			distance_SN = values[3]

			self.pushButton_temperature.setText("{:.1f} °C".format(temperature))
			self.pushButton_humidity.setText("{:.1f} %".format(humidity))

			# Temperature  --------------------------------------------------------------------
			if temperature >= 0 and temperature <= 30:
				self.pushButton_temperature.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")
			elif temperature >= -20 and temperature <= 60:
				self.pushButton_temperature.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
			else:
				self.pushButton_temperature.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")

			# HUMIDITY  --------------------------------------------------------------------
			if humidity < 20:
				self.pushButton_humidity.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")
			elif humidity < 40:
				self.pushButton_humidity.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
			else:
				self.pushButton_humidity.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")
			
			# DISTANCE IR --------------------------------------------------------------------
			if distance_IR > 35 or distance_IR <= 0:
				self.pushButton_ir.setText("∞")
				self.pushButton_ir.setStyleSheet("QPushButton { font-size:16px; color: rgb(0, 0, 0); }")
			else:
				self.pushButton_ir.setStyleSheet("QPushButton { font-size:13px; }")
				self.pushButton_ir.setText("{:.1f} cm".format(distance_IR))

				if distance_IR > 18:
					self.pushButton_ir.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")
				elif distance_IR > 8:
					self.pushButton_ir.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
				else:
					self.pushButton_ir.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")

			# DISTANCE SONAR --------------------------------------------------------------------
			if distance_SN > 200 or distance_SN <= 0:
				self.pushButton_sn.setText("∞")
				self.pushButton_sn.setStyleSheet("QPushButton { font-size:16px; color: rgb(0, 0, 0); }")
				
			else:
				self.pushButton_sn.setStyleSheet("QPushButton { font-size:13px; }")
				self.pushButton_sn.setText("{:.1f} cm".format(distance_SN))

				if distance_SN < 7:
					self.pushButton_sn.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")
				elif distance_SN < 15:
					self.pushButton_sn.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
				else:
					self.pushButton_sn.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")

			if self.showCurveId == 0:
				self.temp_curve.addValue(values[0])
			elif self.showCurveId == 1:
				self.humidity_curve.addValue(values[1])
			elif self.showCurveId == 2:
				self.distance_ir_curve.addValue(values[2])
			elif self.showCurveId == 3:
				self.distance_sn_curve.addValue(values[3])

	def setClient(self, client):
		self.PyRobot_Client = client

	def start_capture(self):
		global capture
		capture = True

		self.Sensors_Capture = Sensors_Capture(self, self.PyRobot_Client)
		self.Sensors_Capture.message_received.connect(self.setValues)
		self.Sensors_Capture.start()

	def stop_capture(self):
		global capture
		capture = False
		self.Sensors_Capture.wait()

	def closeEvent(self, event):
		self.stop_capture()
