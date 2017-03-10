from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys, threading, time, copy, os
from random import randint

# Import windows
from Dialog_NewConnection import Dialog_NewConnection
from Dialog_Sensors import Dialog_Sensors
from Dialog_Help import Dialog_Help
from Frame_Camera import Frame_Camera
from Frame_SensorsCurves import Frame_SensorsCurves

class EventLoop(QThread):

	updateStatusWifi = pyqtSignal(int)
	updateStatusBattery = pyqtSignal(int, bool)

	def __init__(self, parent, client):
		super(EventLoop, self).__init__(parent)
		self.PyRobot_Client = client
		self.stopped = False

	def stop(self):
		self.PyRobot_Client = None
		self.stopped = True
		print("LoopEvent stopped")

	def run(self):
		print("LoopEvent started")

		while self.stopped == False:
			try:

				self.PyRobot_Client.tcp_send("wifi")
				msg_recu = self.PyRobot_Client.tcp_read()

				if msg_recu != None:
					tokens = msg_recu.split(" ")
					if tokens[0] == "wifi":
						self.updateStatusWifi.emit(int(tokens[1]))

					self.updateStatusBattery.emit(80, False)
				time.sleep(1)
				
			except Exception as e:
				print(e)

class PyRobot(QMainWindow):

	Main_Client = None
	Event_Client = None
	Sensors_Client = None
	Engine_Client = None
	Camera_Client = None
	IA_Client = None

	EventLoop = None

	def __init__(self):
		QMainWindow.__init__(self)
		if(os.uname()[0] == "Darwin"):
			uic.loadUi('interfaces_osx/pyRobot.ui', self)
		else:
			uic.loadUi('interfaces_linux/pyRobot.ui', self)
		self.setFocus()

		self.key_pressed = False
		self.lightOn = False
		self.lightMode = 0
		self.autoMode = False

		# Boutons de gestion des entrées
		self.pushButton_new_connection.clicked.connect(self.newConnection)
		self.pushButton_disconnect.clicked.connect(self.disconnect)
		self.pushButton_help.clicked.connect(self.openHelp)
		self.pushButton_sensors.clicked.connect(self.openWindowSensors)
		self.pushButton_enabled_keyboard.clicked.connect(self.setFocus)
		self.pushButton_lights.clicked.connect(self.changeLightState)
		self.pushButton_send_monitor.clicked.connect(self.execute_cmd)
		self.pushButton_automatic.clicked.connect(self.AutomaticMode)

		# Diverses actions
		self.lineEdit_commandline.returnPressed.connect(self.execute_cmd)
		self.verticalSlider_lightsMode.valueChanged.connect(self.changeLightMode)
		self.verticalSlider_enginePower.valueChanged.connect(self.changeEnginePower)
		self.verticalSlider_luminosity.valueChanged.connect(self.changeLuminosity)

		# Setup
		#self.updateStatus()
		self.pushButton_disconnect.setEnabled(False)
		self.pushButton_send_monitor.setEnabled(False)
		self.pushButton_sensors.setEnabled(False)
		self.pushButton_enabled_keyboard.setEnabled(False)
		self.pushButton_lights.setEnabled(False)
		self.pushButton_automatic.setEnabled(False)
		self.pushButton_script.setEnabled(False)
		self.lineEdit_commandline.setEnabled(False)
		self.verticalSlider_lightsMode.setEnabled(False)
		self.verticalSlider_enginePower.setEnabled(False)
		self.verticalSlider_luminosity.setEnabled(False)
		self.printToMonitor("> Welcome to PyRobot !")

		self.frame_camera = Frame_Camera(self, self.Camera_Client)
		self.frame_camera.setEnabled(False)

		self.frame_sensorsCurves = Frame_SensorsCurves(self, self.Sensors_Client)
		self.spacer = QSpacerItem(1,10, QSizePolicy.Preferred, QSizePolicy.Expanding)

		self.frame_sensorsCurves.setEnabled(False)

		self.right_panel.addWidget(self.frame_camera)
		#self.right_panel.addSpacerItem(self.spacer)
		self.right_panel.addWidget(self.frame_sensorsCurves)
		#self.right_panel.addSpacerItem(self.spacer)
		self.right_panel.setSpacing(10)


	def updateStatus(self):
		if self.Main_Client != None:

			self.printToMonitor("Connected to PyRobot at {}:{}".format(self.Main_Client.hote, self.Main_Client.port))

			self.pushButton_disconnect.setEnabled(True)
			self.pushButton_send_monitor.setEnabled(True)
			self.pushButton_sensors.setEnabled(True)
			self.pushButton_enabled_keyboard.setEnabled(True)
			self.pushButton_lights.setEnabled(True)
			self.pushButton_automatic.setEnabled(True)
			self.pushButton_script.setEnabled(True)
			self.lineEdit_commandline.setEnabled(True)
			self.verticalSlider_lightsMode.setEnabled(True)
			self.verticalSlider_enginePower.setEnabled(True)
			self.verticalSlider_luminosity.setEnabled(True)

			self.pushButton_new_connection.setIcon(QIcon(QPixmap(":/resources/img/resources/img/ButtonOk-01.png")))

			self.frame_camera.setClient(self.Camera_Client)
			self.frame_camera.setEnabled(True)

			self.frame_sensorsCurves.setClient(self.Sensors_Client)
			self.frame_sensorsCurves.setEnabled(True)
			self.frame_sensorsCurves.start_capture()

			self.EventLoop = EventLoop(self, self.Event_Client)
			self.EventLoop.updateStatusWifi.connect(self.changeWifiQuality)
			self.EventLoop.updateStatusBattery.connect(self.changeBatteryLevel)
			self.EventLoop.start()

		else:
			self.disconnect()

	def closeEvent(self, event):
		self.disconnect()

	def keyPressEvent(self, event):
		if self.Main_Client != None and self.key_pressed == False:
			self.key_pressed = True

			if event.key() == Qt.Key_Up:
				self.Engine_Client.tcp_send("eng forward")
			elif event.key() == Qt.Key_Down:
				self.Engine_Client.tcp_send("eng backward")
			elif event.key() == Qt.Key_Left:
				self.Engine_Client.tcp_send("eng left")
			elif event.key() == Qt.Key_Right:
				self.Engine_Client.tcp_send("eng right")

			elif event.key() == Qt.Key_Space:
				self.changeLightState()

	def keyReleaseEvent(self, event):
		if self.Engine_Client != None:
			self.key_pressed = False

			if event.key() == Qt.Key_Up:
				self.Engine_Client.tcp_send("eng stop")
			elif event.key() == Qt.Key_Down:
				self.Engine_Client.tcp_send("eng stop")
			elif event.key() == Qt.Key_Left:
				self.Engine_Client.tcp_send("eng stop")
			elif event.key() == Qt.Key_Right:
				self.Engine_Client.tcp_send("eng stop")


	def disconnect(self):
		if self.EventLoop != None:
			self.EventLoop.stop()
			self.EventLoop = None

		if self.Main_Client != None:
			if self.lightOn == True:
				self.changeLightState()

			self.verticalSlider_luminosity.setValue(100)
			self.verticalSlider_enginePower.setValue(100)

			self.Main_Client.tcp_send("fl lum 100")
			self.Main_Client.tcp_send("fl w off")
			self.Main_Client.tcp_send("fl ir off")
			self.IA_Client.tcp_send("ia stop")

			self.frame_sensorsCurves.stop_capture()

			self.Main_Client.close()
			self.Event_Client.close()
			self.Sensors_Client.close()
			self.Engine_Client.close()
			self.Camera_Client.close()
			self.IA_Client.close()

			self.Main_Client = None
			self.Event_Client = None
			self.Sensors_Client = None
			self.Engine_Client = None
			self.Camera_Client = None
			self.IA_Client = None

		self.pushButton_disconnect.setEnabled(False)
		self.pushButton_send_monitor.setEnabled(False)
		self.pushButton_sensors.setEnabled(False)
		self.pushButton_enabled_keyboard.setEnabled(False)
		self.pushButton_lights.setEnabled(False)
		self.pushButton_automatic.setEnabled(False)
		self.pushButton_script.setEnabled(False)
		self.lineEdit_commandline.setEnabled(False)
		self.verticalSlider_lightsMode.setEnabled(False)
		self.verticalSlider_enginePower.setEnabled(False)
		self.verticalSlider_luminosity.setEnabled(False)
		
		self.frame_camera.setEnabled(False)
		self.frame_sensorsCurves.setEnabled(False)

		self.icon_wifi.setPixmap(QPixmap(":/resources/img/resources/img/wifi_off.png"))
		self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-missing.png"))
		self.pushButton_new_connection.setIcon(QIcon(QPixmap(":/resources/img/resources/img/ButtonRSS-01.png")))

		self.printToMonitor("> Connection closed.")

	def newConnection(self):
		new_connection = Dialog_NewConnection()

		if new_connection.exec_():
			self.Main_Client = new_connection.Main_Client
			self.Event_Client = new_connection.Event_Client
			self.Sensors_Client = new_connection.Sensors_Client
			self.Engine_Client = new_connection.Engine_Client
			self.Camera_Client = new_connection.Camera_Client
			self.IA_Client = new_connection.IA_Client

			self.updateStatus()

	def openHelp(self):
		dialog_help = Dialog_Help(self)
		dialog_help.show()

	def openWindowSensors(self):
		sensors = Dialog_Sensors(self, self.Sensors_Client)
		sensors.show()
		sensors.Sensors_Capture.start()
		#sensors.exec_()

	def changeEnginePower(self):
		power = self.verticalSlider_enginePower.value()*10
		self.label_enginePower.setText(str(power)+" %")
		self.Engine_Client.tcp_send("eng speed {}".format(power))

	def changeLuminosity(self):
		luminosity = self.verticalSlider_luminosity.value()*10
		self.label_luminosity.setText(str(luminosity)+" %")
		self.Main_Client.tcp_send("fl lum {}".format(luminosity))

	def changeLightMode(self):
		if self.verticalSlider_lightsMode.value() == 0:
			self.lightMode = 0

			if self.lightOn == True:
				buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/light.png"))
				self.pushButton_lights.setIcon(buttonIcon)
				print("Light WHITE")
				self.Main_Client.tcp_send("fl ir off")
				self.Main_Client.tcp_send("fl w on")

		else:
			self.lightMode = 1

			if self.lightOn == True:
				buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/light-ir.png"))
				self.pushButton_lights.setIcon(buttonIcon)
				print("Light IR")
				self.Main_Client.tcp_send("fl w off")
				self.Main_Client.tcp_send("fl ir on")

	def AutomaticMode(self):
		if self.autoMode == True:
				buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Compass-iPhone-2-icon_OFF.png"))
				self.pushButton_automatic.setIcon(buttonIcon)
				
				self.autoMode = False
				self.IA_Client.tcp_send("ia stop")
				print("AutoMode disabled.")

		else:
				buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/Compass-iPhone-2-icon.png"))
				self.pushButton_automatic.setIcon(buttonIcon)
			
				self.autoMode = True
				self.IA_Client.tcp_send("ia auto")
				print("AutoMode enabled.")


	def changeLightState(self):
		if self.lightOn == False:
			self.lightOn = True

			if self.lightMode == 0:
				buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/light.png"))
				self.pushButton_lights.setIcon(buttonIcon)
				print("Light WHITE")
				self.Main_Client.tcp_send("fl ir off")
				self.Main_Client.tcp_send("fl w on")
			
			elif self.lightMode == 1:
				buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/light-ir.png"))
				self.pushButton_lights.setIcon(buttonIcon)
				print("Light IR")
				self.Main_Client.tcp_send("fl w off")
				self.Main_Client.tcp_send("fl ir on")

		elif self.lightOn == True:
			self.lightOn = False

			buttonIcon = QIcon(QPixmap(":/resources/img/resources/img/light-off.png"))
			self.pushButton_lights.setIcon(buttonIcon)
			print("Light OFF")

			if self.lightMode == 0:
				self.Main_Client.tcp_send("fl w off")
			if self.lightMode == 1:		
				self.Main_Client.tcp_send("fl ir off")
				

	@pyqtSlot(int)
	def changeWifiQuality(self, percentage):
		if percentage < 33:
			self.icon_wifi.setPixmap(QPixmap(":/resources/img/resources/img/wifi_low.png"))
		elif percentage < 66:
			self.icon_wifi.setPixmap(QPixmap(":/resources/img/resources/img/wifi_medium.png"))
		else:
			self.icon_wifi.setPixmap(QPixmap(":/resources/img/resources/img/wifi_high.png"))

		QApplication.processEvents()

	@pyqtSlot(int, bool)
	def changeBatteryLevel(self, percentage, charging):
		if percentage <= 10:
			if not charging:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-10.png"))
			else:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-charging-10.png"))

		elif percentage <= 20:
			if not charging:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-20.png"))
			else:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-charging-20.png"))

		elif percentage <= 40:
			if not charging:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-40.png"))
			else:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-charging-40.png"))

		elif percentage <= 60:
			if not charging:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-60.png"))
			else:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-charging-60.png"))
		elif percentage <= 80:
			if not charging:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-80.png"))
			else:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-charging-80.png"))
		else:
			if not charging:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-100.png"))
			else:
				self.icon_battery.setPixmap(QPixmap(":/resources/img/resources/img/Battery/battery-charging-100.png"))

		QApplication.processEvents()

	def execute_cmd(self):
		cmd = self.lineEdit_commandline.text()

		tokens = cmd.split(" ")

		self.lineEdit_commandline.clear()
		self.printToMonitor("> "+cmd)

		if tokens[0] == "modules":
			self.showModulesList()

		elif tokens[0] == "sled":
			self.Main_Client.tcp_send(cmd)

		elif tokens[0] == "fl":
			if len(tokens) > 1:

				if tokens[1] == "status":
					self.Main_Client.tcp_send(cmd)
					msg_recu = self.Main_Client.tcp_read()

					if msg_recu != None:
						print(msg_recu)
						args = msg_recu.split(" ")
						if args[2] == "True":
							self.printToMonitor("FrontLights : ON ({} %)".format(args[3]))
						else:
							self.printToMonitor("FrontLights : OFF".format(args[3]))

				else:
					self.Main_Client.tcp_send(cmd)

		elif tokens[0] == "sns":
			self.Sensors_Client.tcp_send(cmd)

		elif tokens[0] == "eng":
			self.Engine_Client.tcp_send(cmd)

		elif tokens[0] == "wifi":
			self.Event_Client.tcp_send(cmd)
			msg_recu = self.Event_Client.tcp_read()

			if msg_recu != None:
				args = msg_recu.split(" ")
				self.printToMonitor("Wifi signal : {} %".format(args[1]))
				self.changeWifiQuality(int(args[1]))

		elif tokens[0] == "clear":
			self.plainTextEdit_monitor.clear()
		else:
			self.printToMonitor("Command not found.")

		
	def printToMonitor(self, msg):
		self.plainTextEdit_monitor.moveCursor(QTextCursor.End);
		self.plainTextEdit_monitor.insertPlainText(msg);
		self.plainTextEdit_monitor.appendPlainText("");
		self.plainTextEdit_monitor.verticalScrollBar().setValue(self.plainTextEdit_monitor.verticalScrollBar().maximum())

	def showModulesList(self):
		self.printToMonitor("\n === Installed Modules === \n" \
												+" + FrontLights - fl \n" \
												+" + Sensors - sns \n" \
												+" + Status LED - sled \n" \
												+" + Engine - eng \n")

		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	#app.setStyle(QStyleFactory.create("Fusion"))
	window = PyRobot()
	window.show()
	sys.exit(app.exec_())