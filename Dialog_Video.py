from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc
import socket
from PyRobot_Client import PyRobot_Client

class Dialog_Video(QDialog):

	def __init__(self, client):
		QDialog.__init__(self)
		uic.loadUi('Dialog_Video.ui', self)
