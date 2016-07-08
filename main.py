from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys

qtCreatorFile = "pyRobot.ui"
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class PyRobot(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
 
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PyRobot()
    window.show()
    sys.exit(app.exec_())