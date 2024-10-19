from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDateTime, QDate
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDataWidgetMapper, QDialog, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCalendarWidget, QDateEdit, QComboBox, QCheckBox, QApplication, QFileDialog

from HotkeysTable import HotkeysTable
from HotkeyDialog import HotkeyDialog
from utils import read_json, write_json


class SCPSettingsWindow(QMainWindow):

    '''
    scp -i /home/m.kaplan/m.kaplan_PROD.rsa m.kaplan@extstg3-ums-privil-ase-01.ptstaging.ptec:/opt/local/tmp/server.log.359.20240513-115841-125.zst /home/m.kaplan/
        -RSA file location
        -Username
        -Path to save
    '''

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCP Settings")
        folder_icon = self.style().standardIcon(QApplication.style().SP_DirIcon)

        self.setMinimumSize(450, 325)
        self.resize(450, 250)

        self.data = read_json()
        confRSA = ""
        confUsername = ""
        confDownload = ""
        confHotkey = "None"

        if "scpConf" in self.data:
            confRSA = self.data["scpConf"].get("rsaPath", "")
            confUsername = self.data["scpConf"].get("username", "")
            confDownload = self.data["scpConf"].get("downloadPath", "")
            confHotkey = self.data["scpConf"].get("hotkey", "None")

        mainLayout = QVBoxLayout()

        # RSA file
        rsaRowLayout = QHBoxLayout()
        rsaLabel = QLabel("RSA file: ")
        self.rsaInput = QLineEdit(confRSA)
        self.rsaButton = QPushButton()
        self.rsaButton.setIcon(folder_icon)
        self.rsaButton.clicked.connect(self.getRSAFile)

        rsaRowLayout.addWidget(rsaLabel)
        rsaRowLayout.addWidget(self.rsaInput)
        rsaRowLayout.addWidget(self.rsaButton)

        mainLayout.addLayout(rsaRowLayout)

        # Username
        usernameRowLayout = QHBoxLayout()
        usernameLabel = QLabel("Machine username: ")
        self.usernameInput = QLineEdit(confUsername)
        self.usernameInput.setPlaceholderText("f.e. m.kaplan")

        usernameRowLayout.addWidget(usernameLabel)
        usernameRowLayout.addWidget(self.usernameInput)
        mainLayout.addLayout(usernameRowLayout)

        # Download path
        downloadRowLayout = QHBoxLayout()
        downloadLabel = QLabel("Download path: ")
        self.downloadInput = QLineEdit(confDownload)
        self.downloadButton = QPushButton()
        self.downloadButton.setIcon(folder_icon)
        self.downloadButton.clicked.connect(self.getDownloadPath)

        downloadRowLayout.addWidget(downloadLabel)
        downloadRowLayout.addWidget(self.downloadInput)
        downloadRowLayout.addWidget(self.downloadButton)

        mainLayout.addLayout(downloadRowLayout)

        #Hotkey
        hotkeyRowLayout = QHBoxLayout()
        hotkeyLabel = QLabel("Hotkey: ")
        self.combo_box = QComboBox()
        comboItems =["F"+str(n+1) for n in range(12)]
        comboItems.insert(0, "None")
        self.combo_box.addItems(comboItems)
        self.combo_box.setCurrentIndex(comboItems.index(confHotkey))

        hotkeyRowLayout.addWidget(hotkeyLabel)
        hotkeyRowLayout.addWidget(self.combo_box)

        mainLayout.addLayout(hotkeyRowLayout)

        # Buttons
        okButton = QPushButton("Ok")
        okButton.clicked.connect(self.okayClicked)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancelClicked)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        mainLayout.addLayout(buttonLayout)

        # self
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        layout = QVBoxLayout()
        layout.addWidget(mainWidget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def getRSAFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Open RSA File","", "RSA (*.rsa *.json)")
        self.rsaInput.setText(fileName[0])

    def getDownloadPath(self):
        fileName = QFileDialog.getExistingDirectory(self, "Select Download Directory","", QFileDialog.ShowDirsOnly)
        self.downloadInput.setText(fileName)

    def okayClicked(self):
        scpConf = {
            "rsaPath": self.rsaInput.text(),
            "username": self.usernameInput.text(),
            "downloadPath": self.downloadInput.text(),
            "hotkey": self.combo_box.currentText()
        }

        self.data["scpConf"] = scpConf
        write_json(self.data)
        self.close()

    def cancelClicked(self):
        self.close()