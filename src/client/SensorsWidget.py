from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc
import io
import time

from PyRobot_Client import PyRobot_Client

class SensorsWidget(QFrame):

	def __init__(self, parent):
		QDialog.__init__(self, parent)
		uic.loadUi('interfaces/SensorsWidget.ui', self)

		self.value = 0
		self.unit = ""
		

	def setIcon(self, file):
		self.icon.setPixmap(QPixmap(file))

	def setValue(self, n):
		self.value = n
		self.update()

	def setUnit(self, unit):
		self.unit = unit
		self.update()

	def update(self):
		self.label_value.setText("{} {}".format(self.value, self.unit))

