#!/usr/bin/env python
# --*-- coding: utf-8 --*--

from PyQt4 import QtGui 
from PyQt4 import QtCore 
import os

app_icon_path = os.path.join(os.path.dirname(__file__), 'icons')

class PasswdDialog(QtGui.QDialog):
    def __init__(self, parent=None, message=""):
        super(self.__class__, self).__init__(parent)
        self.resize(350, 150)
        self.setWindowTitle("qvnc")
        self.message = message
        self.messageLabel = QtGui.QLabel(self.message)

        self.passwdLabel = QtGui.QLabel('Password:')
        self.passwdEdit  = QtGui.QLineEdit( )
        self.passwdEdit.setEchoMode(QtGui.QLineEdit.Password)

        self.buttonBox = QtGui.QDialogButtonBox( )
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)

        self.groupBox = QtGui.QGroupBox( )
        self.layout = QtGui.QGridLayout( )
        #self.layout.addWidget(self.messageLabel, 0, 0)
        self.layout.addWidget(QtGui.QLabel(""),  0, 0)
        self.layout.addWidget(self.passwdLabel,  0, 0)
        self.layout.addWidget(self.passwdEdit,   0, 2)
        self.groupBox.setLayout(self.layout)
        self.mainLayout = QtGui.QVBoxLayout( )
        self.mainLayout.addWidget(self.messageLabel)
        self.mainLayout.addWidget(self.groupBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.mainLayout.setSpacing(10)
        self.mainLayout.setMargin(10)
        self.setLayout(self.mainLayout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.show( )
        self.isAccepted = self.exec_( ) 


class ConnectDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.resize(350,200)
        self.setWindowTitle("qvnc")

        self.iconImage   = QtGui.QImage(os.path.join(app_icon_path, "vnc_connect.png"))
        
        self.serverLabel = QtGui.QLabel("VNC Server")
        self.speedLabel  = QtGui.QLabel("Speed")

        self.serverEdit = QtGui.QLineEdit( )
        self.speedCombo = QtGui.QComboBox( )
        self.speedCombo.addItem("fast")
        self.speedCombo.addItem("middle")
        self.speedCombo.addItem("low")

        self.buttonBox    = QtGui.QDialogButtonBox( )
        self.optionButton = QtGui.QPushButton("Option")
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText("Connect")

        self.gridLayout = QtGui.QGridLayout( )
        self.gridLayout.addWidget(QtGui.QLabel(""), 0, 0)
        self.gridLayout.addWidget(self.serverLabel, 1, 1)
        self.gridLayout.addWidget(self.serverEdit,  1, 2)
        self.gridLayout.addWidget(self.speedLabel,  2, 1)
        self.gridLayout.addWidget(self.speedCombo,  2, 2)

        self.hboxLayout = QtGui.QHBoxLayout( )
        self.hboxLayout.addWidget(self.optionButton)
        self.hboxLayout.addWidget(self.buttonBox)

        self.mainLayout = QtGui.QVBoxLayout( )
        self.mainLayout.addLayout(self.gridLayout)
        self.mainLayout.addLayout(self.hboxLayout)
        self.mainLayout.setMargin(10)
        self.mainLayout.setSpacing(10)
        self.setLayout(self.mainLayout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.optionButton.clicked.connect(self.onOption)
        self.show( )
        self.isAccepted = self.exec_( ) 

    def paintEvent(self, event):
        qp = QtGui.QPainter( )
        qp.begin(self)
        qp.drawImage(140, 10, self.iconImage)
        qp.end( )

    def onOption(self):
        pass

def passwdDialog(parent=None, message=""):
    res = PasswdDialog(parent, message)
    if not res.isAccepted:
        return
    else:
        return str(res.passwdEdit.text().toUtf8())

def connectDialog(parent=None):
    res = ConnectDialog(parent)
    if not res.isAccepted:
        return
    else:
        res = (str(res.serverEdit.text().toUtf8()), 
               str(res.speedCombo.currentText().toUtf8()))
        return res
