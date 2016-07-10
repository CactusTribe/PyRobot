from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys, threading

# Import windows
from Dialog_NewConnection import Dialog_NewConnection

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
		self.pushButton_send_monitor.clicked.connect(self.execute_cmd)
		self.lineEdit_commandline.returnPressed.connect(self.execute_cmd)

		# Setup
		self.updateStatus()
		self.pushButton_send_monitor.setEnabled(False)
		self.lineEdit_commandline.setEnabled(False)

		# Threads
		self.listeningServeur = None 

	def newConnection(self):
		new_connection = Dialog_NewConnection()

		if new_connection.exec_():
			self.PyRobot_Client = new_connection.PyRobot_Client
			self.updateStatus()

	def tcp_listening(self):
		while self.PyRobot_Client.connected == True:
			msg_recu = self.PyRobot_Client.tcp_read()
			if msg_recu != None: 
				#print(msg_recu)
				self.plainTextEdit_monitor.moveCursor(QTextCursor.End)
				self.plainTextEdit_monitor.insertPlainText(msg_recu+"\n")

	def updateStatus(self):
		if self.PyRobot_Client != None:
			if self.PyRobot_Client.connected == False:
				self.label_ip.setText("No connection")
				self.pushButton_send_monitor.setEnabled(False)
				self.lineEdit_commandline.setEnabled(False)
			else:
				self.label_ip.setText(self.PyRobot_Client.hote)
				self.plainTextEdit_monitor.moveCursor(QTextCursor.End)
				self.plainTextEdit_monitor.insertPlainText("Connected to PyRobot at {}:{}\n".format(self.PyRobot_Client.hote, self.PyRobot_Client.port))
				self.pushButton_send_monitor.setEnabled(True)
				self.lineEdit_commandline.setEnabled(True)

				self.listeningServeur = threading.Thread(target=self.tcp_listening)
				self.listeningServeur.start()

	def execute_cmd(self):
		cmd = self.lineEdit_commandline.text()
		tokens = cmd.split(" ")

		self.plainTextEdit_monitor.moveCursor(QTextCursor.End)
		self.plainTextEdit_monitor.insertPlainText("> "+cmd+"\n")
		self.lineEdit_commandline.clear()

		if tokens[0] == "led":
			if len(tokens) > 1:
				if tokens[1] == "red":
					self.PyRobot_Client.tcp_send("red")
				elif tokens[1] == "green":
					self.PyRobot_Client.tcp_send("green")
				elif tokens[1] == "blue":
					self.PyRobot_Client.tcp_send("blue")

		elif tokens[0] == "rgb":
			self.PyRobot_Client.tcp_send(cmd)

		elif tokens[0] == "lg":
			self.PyRobot_Client.tcp_send(cmd)

		elif tokens[0] == "flash":
			self.PyRobot_Client.tcp_send(cmd)
			
		elif tokens[0] == "clear":
			self.plainTextEdit_monitor.clear()
		else:
			self.plainTextEdit_monitor.insertPlainText("Command not found.\n")


	def sendMsg(self):
		self.PyRobot_Client.tcp_send(self.lineEdit_commandline.text())
		

	def closeEvent(self, event):
		self.PyRobot_Client.close()
		

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = PyRobot()
	window.show()
	sys.exit(app.exec_())