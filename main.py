from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys

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
		self.pushButton_send_monitor.clicked.connect(self.sendMsg)
		self.lineEdit_commandline.returnPressed.connect(self.sendMsg)

		# Setup
		self.updateStatus()
		self.pushButton_send_monitor.setEnabled(False)
		self.lineEdit_commandline.setEnabled(False)

	def newConnection(self):
		new_connection = Dialog_NewConnection()

		if new_connection.exec_():
			self.PyRobot_Client = new_connection.PyRobot_Client
			self.updateStatus()

	def updateStatus(self):
		if self.PyRobot_Client != None:
			if self.PyRobot_Client.connected == False:
				self.label_ip.setText("No connection")
				self.pushButton_send_monitor.setEnabled(False)
				self.lineEdit_commandline.setEnabled(False)
			else:
				self.label_ip.setText(self.PyRobot_Client.hote)
				self.plainTextEdit_monitor.moveCursor(QTextCursor.End)
				self.plainTextEdit_monitor.insertPlainText("> Connected to PyRobot at {}:{}\n".format(self.PyRobot_Client.hote, self.PyRobot_Client.port))
				self.pushButton_send_monitor.setEnabled(True)
				self.lineEdit_commandline.setEnabled(True)

	def sendMsg(self):
		self.plainTextEdit_monitor.moveCursor(QTextCursor.End)
		self.plainTextEdit_monitor.insertPlainText("# "+self.lineEdit_commandline.text()+"\n")
		self.PyRobot_Client.tcp_send(self.lineEdit_commandline.text())
		self.lineEdit_commandline.clear()
		

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = PyRobot()
	window.show()
	sys.exit(app.exec_())