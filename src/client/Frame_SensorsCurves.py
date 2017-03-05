from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc
import io
import time

from PyRobot_Client import PyRobot_Client
from SensorsWidget import SensorsWidget
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
		uic.loadUi('interfaces/Frame_SensorsCurves.ui', self)
		self.PyRobot_Client = client

		global capture
		capture = True

		self.Sensors_Capture = Sensors_Capture(self, self.PyRobot_Client)
		self.Sensors_Capture.message_received.connect(self.setValues)

		self.layout_widget = QGridLayout()
		self.layout_widget.setVerticalSpacing(5);
		self.layout_widget.setHorizontalSpacing(0);

		self.buttonWidth = 130

		self.w_temperature = QPushButton("{} °C".format(0))
		self.w_temperature.setMinimumHeight(50)
		self.w_temperature.setMinimumWidth(self.buttonWidth)
		self.w_temperature.setMaximumWidth(self.buttonWidth)
		self.w_temperature.setIconSize(QSize(30,30))
		self.w_temperature.setIcon(QIcon(":/resources/img/resources/img/Thermometer_Snowflake.png"))

		self.w_humidity = QPushButton("{} %".format(0))
		self.w_humidity.setMinimumHeight(50)
		self.w_humidity.setMinimumWidth(self.buttonWidth)
		self.w_humidity.setMaximumWidth(self.buttonWidth)
		self.w_humidity.setIconSize(QSize(30,30))
		self.w_humidity.setIcon(QIcon(":/resources/img/resources/img/humidity.png"))

		self.w_distance_IR = QPushButton("{} cm".format(0))
		self.w_distance_IR.setMinimumHeight(50)
		self.w_distance_IR.setMinimumWidth(self.buttonWidth)
		self.w_distance_IR.setMaximumWidth(self.buttonWidth)
		self.w_distance_IR.setIconSize(QSize(30,30))
		self.w_distance_IR.setIcon(QIcon(":/resources/img/resources/img/laser1.png"))

		self.w_distance_SN = QPushButton("{} cm".format(0))
		self.w_distance_SN.setMinimumHeight(50)
		self.w_distance_SN.setMinimumWidth(self.buttonWidth)
		self.w_distance_SN.setMaximumWidth(self.buttonWidth)
		self.w_distance_SN.setIconSize(QSize(30,30))
		self.w_distance_SN.setIcon(QIcon(":/resources/img/resources/img/radar1.png"))

		self.w_temperature.clicked.connect(self.showTempCurve)
		self.w_humidity.clicked.connect(self.showHumidityCurve)
		self.w_distance_IR.clicked.connect(self.showIRCurve)
		self.w_distance_SN.clicked.connect(self.showSNCurve)

		self.font = self.w_temperature.font()
		self.font.setPointSize(13)
		self.font.setBold(True)
		self.font.setItalic(True)

		self.w_temperature.setFont(self.font)
		self.w_humidity.setFont(self.font)
		self.w_distance_IR.setFont(self.font)
		self.w_distance_SN.setFont(self.font)
		
		self.layout_widget.addWidget(self.w_temperature)
		self.layout_widget.addWidget(self.w_humidity)
		self.layout_widget.addWidget(self.w_distance_IR)
		self.layout_widget.addWidget(self.w_distance_SN)

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
		#self.temp_curve.hide()

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
		self.distance_sn_curve.setMaximum(450)
		self.distance_sn_curve.hide()

		self.right_panel_bottom = QHBoxLayout()
		self.right_panel_bottom.setContentsMargins(0,0,0,0)
		self.right_panel_bottom.setSpacing(5)
		self.right_panel_bottom.addLayout(self.layout_widget)

		self.right_panel_bottom.addWidget(self.temp_curve)
		self.right_panel_bottom.addWidget(self.humidity_curve)
		self.right_panel_bottom.addWidget(self.distance_ir_curve)
		self.right_panel_bottom.addWidget(self.distance_sn_curve)

		self.setLayout(self.right_panel_bottom)

	def showTempCurve(self):
		self.temp_curve.show()
		self.humidity_curve.hide()
		self.distance_ir_curve.hide()
		self.distance_sn_curve.hide()

	def showHumidityCurve(self):
		self.temp_curve.hide()
		self.humidity_curve.show()
		self.distance_ir_curve.hide()
		self.distance_sn_curve.hide()

	def showIRCurve(self):
		self.temp_curve.hide()
		self.humidity_curve.hide()
		self.distance_ir_curve.show()
		self.distance_sn_curve.hide()

	def showSNCurve(self):
		self.temp_curve.hide()
		self.humidity_curve.hide()
		self.distance_ir_curve.hide()
		self.distance_sn_curve.show()

	@pyqtSlot(list)
	def setValues(self, values):

		temperature = values[0]
		humidity = values[1]
		distance_IR = values[2]
		distance_SN = values[3]

		self.w_temperature.setText("{:.1f} °C".format(temperature))
		self.w_humidity.setText("{:.1f} %".format(humidity))
		self.w_distance_IR.setText("{:.1f} cm".format(distance_IR))

		# Temperature  --------------------------------------------------------------------
		if temperature >= 0 and temperature <= 30:
			self.w_temperature.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")
		elif temperature >= -20 and temperature <= 60:
			self.w_temperature.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
		else:
			self.w_temperature.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")

		# HUMIDITY  --------------------------------------------------------------------
		if humidity < 20:
			self.w_humidity.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")
		elif humidity < 40:
			self.w_humidity.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
		else:
			self.w_humidity.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")
		
		# DISTANCE IR --------------------------------------------------------------------
		if distance_IR > 35 or distance_IR <= 0:
			self.w_distance_IR.setText("∞")
			self.w_distance_IR.setStyleSheet("QPushButton { font-size:16px; color: rgb(0, 0, 0); }")
		else:
			self.w_distance_IR.setStyleSheet("QPushButton { font-size:13px; }")
			self.w_distance_IR.setText("{:.1f} cm".format(distance_IR))

			if distance_IR > 18:
				self.w_distance_IR.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")
			elif distance_IR > 8:
				self.w_distance_IR.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
			else:
				self.w_distance_IR.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")

		# DISTANCE SONAR --------------------------------------------------------------------
		if distance_SN > 450 or distance_SN <= 0:
			self.w_distance_SN.setText("∞")
			self.w_distance_SN.setStyleSheet("QPushButton { font-size:16px; color: rgb(0, 0, 0); }")
			
		else:
			self.w_distance_SN.setStyleSheet("QPushButton { font-size:13px; }")
			self.w_distance_SN.setText("{:.1f} cm".format(distance_SN))

			if distance_SN < 7:
				self.w_distance_SN.setStyleSheet("QPushButton { color: rgb(255, 0, 0) }")
			elif distance_SN < 15:
				self.w_distance_SN.setStyleSheet("QPushButton { color: rgb(255, 150, 0) }")
			else:
				self.w_distance_SN.setStyleSheet("QPushButton { color: rgb(0, 180, 0) }")

		
		self.temp_curve.addValue(values[0])
		self.humidity_curve.addValue(values[1])
		self.distance_ir_curve.addValue(values[2])
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
