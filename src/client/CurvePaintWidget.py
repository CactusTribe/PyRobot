from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

import math


class CurvePaintWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        #self.setGeometry(300, 300, 280, 170)
        #self.show()
        self.curve = []
        self.unit = ""
        self.minimum = 0
        self.maximum = 100
        self.medium = int((self.maximum + self.minimum) / 2)
        self.dx = 1 # le pas de l'axe X
        self.dy = 1 # le pas de l'axe Y
        self.centeredY = False
        self.colors = {}

    def addValue(self, value):
        self.curve += [value]
        self.update()

    def addColorSet(self, dic_colors):
        self.colors = dic_colors
        
    def setUnit(self, unit):
        self.unit = unit

    def setMinimum(self, value):
        self.minimum = value
        self.medium = int((self.maximum + self.minimum) / 2)

    def setMaximum(self, value):
        self.maximum = value
        self.medium = int((self.maximum + self.minimum) / 2)

    def setPasX(self, value):
        self.dx = value

    def setPasY(self, value):
        self.dy = value

    def setCenteredY(self, value):
        self.centeredY = value

    def paintEvent(self, event):
        echelle = (self.height()/(self.maximum + self.minimum))

        qp = QPainter()
        qp.begin(self)

        # FOND
        brush = QBrush(QColor(0, 0, 0, 30))
        qp.fillRect(0, 0, self.width(), self.height(), brush)

        # REPERE
        pen = QPen(QColor(0,0,0,130), 1, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin)
        qp.setPen(pen)
        qp.drawLine(0, self.height()/2, self.width(), self.height()/2)

        # LEGENDE
        qp.setFont(QFont('Decorative', 9, -1, True))
        qp.drawText(5,5,50,20, Qt.AlignLeft, "{} {}".format(self.maximum, self.unit))
        qp.drawText(5,(self.height()/2)-15,20,20, Qt.AlignLeft, "{}".format(self.medium))  
        qp.drawText(5,self.height()-15,20,20, Qt.AlignLeft, "{}".format(self.minimum))  


        # CURVE
        pen = QPen(QColor("#239fb5"), self.dx, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin)
        qp.setPen(pen)

        nb_samples = int(self.width() / self.dx)

        for e in range(nb_samples):
            current_value = 0
            pos_Y = 0

            if len(self.curve) <= nb_samples:
                if e < len(self.curve):
                    current_value = self.curve[e]
                    pos_Y = self.height() - (current_value * echelle)

            elif len(self.curve) > nb_samples:
                current_value = self.curve[len(self.curve) - (nb_samples - e)]
                pos_Y = self.height() - (current_value * echelle)

            else: break
            
            for key, value in self.colors.items():
                if current_value != 0 and current_value >= key[0] and current_value <= key[1]:
                    pen = QPen(value, self.dx, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin)
                    qp.setPen(pen)
                    #qp.setBrush(value)
                    #qp.drawEllipse(e*self.dx, pos_Y, 1, 1)
                    qp.drawLine(e*self.dx, pos_Y, e*self.dx, self.height())

        qp.end()
