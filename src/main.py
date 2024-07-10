import sys, os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QItemSelection, QModelIndex
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from pynput import keyboard

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TableModel import TableModel
from utils import getSiteIps, getSites, make_combo_box_searchable, openSSH, openCSSH, filterIps, read_json
from HotkeyWindow import HotkeyWindow

MAIN_TABLE_HEADER = ["Ip", "Name"]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        combo = QtWidgets.QComboBox()
        self.sites = getSites()
        self.site = self.sites[0]
        combo.addItems(self.sites)
        make_combo_box_searchable(combo)
        combo.currentIndexChanged.connect(self.siteComboChanged)

        upperLayout = QHBoxLayout()
        upperLayout.addWidget(combo, 50)

        lineEdit = QtWidgets.QLineEdit()
        lineEdit.textChanged.connect(self.filterMachines)

        upperLayout.addWidget(lineEdit, 50)

        upperWidget = QtWidgets.QWidget()
        upperWidget.setLayout(upperLayout)

        layout.addWidget(upperWidget)

        self.data = getSiteIps(self.site)

        self.table = QtWidgets.QTableView()

        self.model = TableModel(self.data, ["IP", "Name"])
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)

        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # self.table.selectionModel().selectionChanged.connect(self.selectionChanged)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.table.doubleClicked.connect(self.startSingleConnection)

        layout.addWidget(self.table)

        lowerLayout = QHBoxLayout()

        hotkeysButton = QtWidgets.QPushButton("Hotkeys")
        hotkeysButton.clicked.connect(self.openHotkeyWindow)

        newPSButton = QtWidgets.QPushButton("New PS")
        newPSButton.clicked.connect(self.startParallelSession)

        lowerLayout.addWidget(hotkeysButton)
        lowerLayout.addWidget(newPSButton)

        lowerWidget = QtWidgets.QWidget()
        lowerWidget.setLayout(lowerLayout)
        layout.addWidget(lowerWidget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.adjustWindowSize()

        self.controller = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.onKeyPress)
        self.listener.start()

    def onKeyPress(self, event):
        try:
            if event.name[0] != "f":
                return

            for hotkey in read_json()["hotkeys"]:
                if str(hotkey[2]).lower() == event.name.lower() and hotkey[1]:
                    print(hotkey[2] + "pressed")
                    self.controller.type(hotkey[0])
        except Exception as e:
            print(f"error: {e}")

    def startSingleConnection(self, index: QModelIndex) -> None:
        ip = self.data[index.row()][0]
        openSSH(ip)

    def startParallelSession(self):
        selected = self.table.selectedIndexes()

        if len(selected) > 0:
            openCSSH(list(set([self.data[index.row()][0] for index in selected])))

    def openHotkeyWindow(self):
        self.w = HotkeyWindow()
        self.w.show()

    def siteComboChanged(self, index):
        print(self.sites[index])
        self.site = self.sites[index]
        self.data = getSiteIps(self.site)
        self.model = TableModel(self.data, MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def filterMachines(self, s):
        self.data = filterIps(self.data, s)
        self.model = TableModel(self.data, MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def adjustWindowSize(self):
        width = self.table.verticalHeader().width() + self.table.horizontalHeader().length() + self.table.frameWidth() * 2 + 40
        height = self.table.horizontalHeader().height() + self.table.verticalHeader().length() + self.table.frameWidth() * 2 + 20
        # self.setMinimumSize(width, height if height < 920 else 920)
        self.resize(width+150, height if height < 920 else 920)

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        for index in selected.indexes():
            print(f'Selected: row {index.row()}, column {index.column()}, value: {index.data()}')

        for index in deselected.indexes():
            print(f'Deselected: row {index.row()}, column {index.column()}, value: {index.data()}')

    def closeEvent(self, event):
        # Unhook all key listeners when closing the window
        self.listener.stop()
        event.accept()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
