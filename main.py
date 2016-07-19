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

		#Boutons de gestion des entrées
		self.pushButton_new_connection.clicked.connect(self.newConnection)
		self.pushButton_sensors.clicked.connect(self.openWindowSensors)
		self.pushButton_send_monitor.clicked.connect(self.execute_cmd)
		self.lineEdit_commandline.returnPressed.connect(self.execute_cmd)

		# Setup
		self.updateStatus()
		self.pushButton_send_monitor.setEnabled(False)
		self.pushButton_sensors.setEnabled(False)
		self.lineEdit_commandline.setEnabled(False)
		self.printToMonitor("> Welcome to PyRobot !")

		# Threads
		self.listeningServeur = None 

	def newConnection(self):
		new_connection = Dialog_NewConnection()

		if new_connection.exec_():
			self.PyRobot_Client = new_connection.PyRobot_Client
			self.updateStatus()

	def openWindowSensors(self):
		sensors = Dialog_Sensors(self.PyRobot_Client)
		sensors.exec_()


	def tcp_listening(self):
		while self.PyRobot_Client.connected == True:
			msg_recu = self.PyRobot_Client.tcp_read()
			if msg_recu != None: 
				tokens = msg_recu.split(" ")

				if tokens[0] == "sns":
					if len(tokens) > 2:
						self.printToMonitor("CH{} : {} ( {}% )".format(tokens[1], tokens[2], int(int(tokens[2])*100/1024) ))
						#self.plainTextEdit_monitor.appendPlainText("CH {} : {}".format(tokens[1], tokens[2]))
						#self.plainTextEdit_monitor.verticalScrollBar().setValue(self.plainTextEdit_monitor.verticalScrollBar().maximum())
				if tokens[0] == "fl":
					if tokens[2] == "True":
						self.printToMonitor("FrontLights : ON (Luminosity : {}%)".format(tokens[3]))
					else:
						self.printToMonitor("FrontLights : OFF (Luminosity : {}%)".format(tokens[3]))

	def updateStatus(self):
		if self.PyRobot_Client != None:
			if self.PyRobot_Client.connected == False:
				self.label_ip.setText("No connection")
				self.pushButton_send_monitor.setEnabled(False)
				self.pushButton_sensors.setEnabled(False)
				self.lineEdit_commandline.setEnabled(False)
			else:
				self.label_ip.setText(self.PyRobot_Client.hote)
				self.printToMonitor("Connected to PyRobot at {}:{}".format(self.PyRobot_Client.hote, self.PyRobot_Client.port))
				#self.plainTextEdit_monitor.appendPlainText("Connected to PyRobot at {}:{}".format(self.PyRobot_Client.hote, self.PyRobot_Client.port))
				self.pushButton_send_monitor.setEnabled(True)
				self.pushButton_sensors.setEnabled(True)
				self.lineEdit_commandline.setEnabled(True)

				self.listeningServeur = threading.Thread(target=self.tcp_listening)
				#self.listeningServeur.start()

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
							print("FrontLights : ON ({} %)".format(args[3]))
							self.printToMonitor("FrontLights : ON ({} %)".format(args[3]))
						else:
							print("FrontLights : OFF".format(args[3]))
							self.printToMonitor("FrontLights : OFF".format(args[3]))

				else:
					self.PyRobot_Client.tcp_send(cmd)

		elif tokens[0] == "sns":
			self.PyRobot_Client.tcp_send(cmd)
			
		elif tokens[0] == "clear":
			self.plainTextEdit_monitor.clear()
		else:
			self.printToMonitor("Command not found.")
			#self.plainTextEdit_monitor.appendPlainText("Command not found.")

		#self.plainTextEdit_monitor.verticalScrollBar().setValue(self.plainTextEdit_monitor.verticalScrollBar().maximum())

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
												+" + Sensors - sns \n")

	def closeEvent(self, event):
		if self.PyRobot_Client != None:
			self.PyRobot_Client.close()
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = PyRobot()
	window.show()
	sys.exit(app.exec_())