from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDateTime, QDate
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDataWidgetMapper, QDialog, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCalendarWidget, QDateEdit, QComboBox, QCheckBox, QApplication

from HotkeysTable import HotkeysTable
from HotkeyDialog import HotkeyDialog
from utils import read_json, write_json


class GrepWindow(QMainWindow):
    '''
    Can choose:
        -Grep type (zstd, z, normal)
        -Case sensitive or not
        -Pattern
        -Date file
        -Add less or not
    '''
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grep")

        self.setMinimumSize(450, 325)
        self.resize(450, 250)

        self.grepOptionIndex = 0
        self.sensitive = True
        self.pattern = " "
        self.result = ""
        self.date = QDateTime.currentDateTime().toString("MMdd")
        self.less = True

        mainLayout = QVBoxLayout()

        # Grep type (zstd, z, normal)
        self.grepTypeSelector = QComboBox()
        self.grepOptions = ["zstdgrep", "zgrep", "grep"]
        self.grepTypeSelector.addItems(self.grepOptions)
        self.grepTypeSelector.currentIndexChanged.connect(self.grepTypeChanged)

        mainLayout.addWidget(QLabel("Grep type:"))
        mainLayout.addWidget(self.grepTypeSelector)

        # Case-sensitive or not
        self.grepCaseSensitivenessCheckbox = QCheckBox("Case sensitive")
        self.grepCaseSensitivenessCheckbox.setChecked(True)
        self.grepCaseSensitivenessCheckbox.stateChanged.connect(self.sensitivenessChanged)

        mainLayout.addWidget(self.grepCaseSensitivenessCheckbox)

        # Pattern
        self.patternInput = QLineEdit()
        self.patternInput.textChanged.connect(self.patternChanged)

        mainLayout.addWidget(QLabel("Pattern:"))
        mainLayout.addWidget(self.patternInput)

        # Date
        self.dateEdit = QDateEdit()
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDateTime(QDateTime.currentDateTime())
        self.dateEdit.dateChanged.connect(self.dateChanged)

        mainLayout.addWidget(QLabel("Date:"))
        mainLayout.addWidget(self.dateEdit)

        # less or not
        self.lessCheckbox = QCheckBox("less")
        self.lessCheckbox.setChecked(True)
        self.lessCheckbox.stateChanged.connect(self.lessChanged)

        mainLayout.addWidget(self.lessCheckbox)

        # Rest
        self.result = ""
        self.resultLabel = QLabel(self.result)
        mainLayout.addWidget(self.resultLabel)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        okButton = QPushButton("Ok")
        okButton.clicked.connect(self.okayClicked)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancelClicked)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        buttonsWidget = QWidget()
        buttonsWidget.setLayout(buttonLayout)

        layout = QVBoxLayout()
        layout.addWidget(mainWidget)
        layout.addWidget(buttonsWidget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.updateResult("", "")

    def grepTypeChanged(self, index):
        self.grepOptionIndex = index
        self.updateResult(self.pattern, self.date)

    def sensitivenessChanged(self, index):
        self.sensitive = index == 2
        self.updateResult(self.pattern, self.date)
    def patternChanged(self, pattern):
        self.updateResult(pattern, self.date)

    def dateChanged(self, date: QDate):
        self.updateResult(self.pattern, date.toString("MMdd"))

    def lessChanged(self, index):
        self.less = index == 2
        self.updateResult(self.pattern, self.date)

    def updateResult(self, pattern: str, date: str):
        self.pattern = pattern if pattern != "" else self.pattern
        self.date = date if date != "" else self.date

        self.result = f"{self.grepOptions[self.grepOptionIndex]} {'-i' if self.sensitive else ''} '{self.pattern}' *{self.date}-* {'| less' if self.less else ''}"
        self.resultLabel.setText(self.result)

    def okayClicked(self):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.result, mode=cb.Clipboard)
        self.close()

    def cancelClicked(self):
        self.close()

