from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys, threading, time

# Import windows
from Dialog_NewConnection import Dialog_NewConnection
from Dialog_Sensors import Dialog_Sensors

qtCreatorFile = "pyRobot.ui" 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class PyRobot(QMainWindow, Ui_MainWindow):

	PyRobot_Client = None

	def __init__(self):
		QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.setFocus()

		self.key_pressed = False
		self.ligthsON = False

		#Boutons de gestion des entrées
		self.pushButton_new_connection.clicked.connect(self.newConnection)
		self.pushButton_sensors.clicked.connect(self.openWindowSensors)
		self.pushButton_enabled_keyboard.clicked.connect(self.setFocus)
		self.pushButton_lights.clicked.connect(self.changeLightState)
		self.pushButton_send_monitor.clicked.connect(self.execute_cmd)
		self.lineEdit_commandline.returnPressed.connect(self.execute_cmd)

		# Setup
		self.updateStatus()
		self.pushButton_send_monitor.setEnabled(False)
		self.pushButton_sensors.setEnabled(False)
		self.pushButton_enabled_keyboard.setEnabled(False)
		self.pushButton_lights.setEnabled(False)
		self.lineEdit_commandline.setEnabled(False)
		self.printToMonitor("> Welcome to PyRobot !")

		# Threads


	def keyPressEvent(self, event):
		if self.PyRobot_Client != None and self.key_pressed == False:
			self.key_pressed = True

			if event.key() == Qt.Key_Up:
				self.PyRobot_Client.tcp_send("eng forward")
			elif event.key() == Qt.Key_Down:
				self.PyRobot_Client.tcp_send("eng backward")
			elif event.key() == Qt.Key_Left:
				self.PyRobot_Client.tcp_send("eng left")
			elif event.key() == Qt.Key_Right:
				self.PyRobot_Client.tcp_send("eng right")

	def keyReleaseEvent(self, event):
		if self.PyRobot_Client != None:
			self.key_pressed = False

			if event.key() == Qt.Key_Up:
				self.PyRobot_Client.tcp_send("eng stop")
			elif event.key() == Qt.Key_Down:
				self.PyRobot_Client.tcp_send("eng stop")
			elif event.key() == Qt.Key_Left:
				self.PyRobot_Client.tcp_send("eng stop")
			elif event.key() == Qt.Key_Right:
				self.PyRobot_Client.tcp_send("eng stop")

	def newConnection(self):
		new_connection = Dialog_NewConnection()

		if new_connection.exec_():
			self.PyRobot_Client = new_connection.PyRobot_Client
			self.updateStatus()

	def openWindowSensors(self):
		sensors = Dialog_Sensors(self.PyRobot_Client)
		sensors.exec_()

	def changeLightState(self):
		if self.ligthsON == False:
			self.ligthsON = True

			sun = QPixmap(":/resources/img/resources/img/Sun-icon.png");
			buttonIcon = QIcon(sun)
			self.pushButton_lights.setIcon(buttonIcon)

			self.PyRobot_Client.tcp_send("fl on")
		else:
			self.ligthsON = False

			moon = QPixmap(":/resources/img/resources/img/Moon-icon.png");
			buttonIcon = QIcon(moon)
			self.pushButton_lights.setIcon(buttonIcon)

			self.PyRobot_Client.tcp_send("fl off")

	
	def updateStatus(self):
		if self.PyRobot_Client != None:
			if self.PyRobot_Client.connected == False:
				self.label_ip.setText("No connection")
				self.pushButton_send_monitor.setEnabled(False)
				self.pushButton_sensors.setEnabled(False)
				self.pushButton_enabled_keyboard.setEnabled(False)
				self.pushButton_lights.setEnabled(False)
				self.lineEdit_commandline.setEnabled(False)
			else:
				self.label_ip.setText(self.PyRobot_Client.hote)
				self.printToMonitor("Connected to PyRobot at {}:{}".format(self.PyRobot_Client.hote, self.PyRobot_Client.port))
	
				self.pushButton_send_monitor.setEnabled(True)
				self.pushButton_sensors.setEnabled(True)
				self.pushButton_enabled_keyboard.setEnabled(True)
				self.pushButton_lights.setEnabled(True)
				self.lineEdit_commandline.setEnabled(True)

	def execute_cmd(self):
		cmd = self.lineEdit_commandline.text()
		tokens = cmd.split(" ")

		self.lineEdit_commandline.clear()
		self.printToMonitor("> "+cmd)

		if tokens[0] == "modules":
			self.showModulesList()

		elif tokens[0] == "sled":
			self.PyRobot_Client.tcp_send(cmd)

		elif tokens[0] == "fl":
			if len(tokens) > 1:

				if tokens[1] == "status":
					self.PyRobot_Client.tcp_send(cmd)
					msg_recu = self.PyRobot_Client.tcp_read()

					if msg_recu != None:
						print(msg_recu)
						args = msg_recu.split(" ")
						if args[2] == "True":
							self.printToMonitor("FrontLights : ON ({} %)".format(args[3]))
						else:
							self.printToMonitor("FrontLights : OFF".format(args[3]))

				else:
					self.PyRobot_Client.tcp_send(cmd)

		elif tokens[0] == "sns":
			self.PyRobot_Client.tcp_send(cmd)

		elif tokens[0] == "eng":
			self.PyRobot_Client.tcp_send(cmd)
			
		elif tokens[0] == "clear":
			self.plainTextEdit_monitor.clear()
		else:
			self.printToMonitor("Command not found.")


	def sendMsg(self):
		self.PyRobot_Client.tcp_send(self.lineEdit_commandline.text())
		
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

	def closeEvent(self, event):
		if self.PyRobot_Client != None:
			self.PyRobot_Client.close()
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = PyRobot()
	window.show()
	sys.exit(app.exec_())