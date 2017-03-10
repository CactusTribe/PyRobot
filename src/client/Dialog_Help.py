from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import os
import resources_rc

class Dialog_Help(QDialog):

	def __init__(self, parent):
		QDialog.__init__(self, parent)
		if(os.uname()[0] == "Darwin"):
			uic.loadUi('interfaces_osx/Dialog_Help.ui', self)
		else:
			uic.loadUi('interfaces_linux/Dialog_Help.ui', self)



	def closeEvent(self, event):
		print("Stop Help")

