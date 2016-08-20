from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import resources_rc

class Dialog_Help(QDialog):

	def __init__(self, parent):
		QDialog.__init__(self, parent)
		uic.loadUi('Dialog_Help.ui', self)


	def closeEvent(self, event):
		print("Stop Help")

