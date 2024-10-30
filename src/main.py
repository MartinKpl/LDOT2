import sys, os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QItemSelection, QModelIndex, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication, QToolBar, QAction
from pynput import keyboard
from pyqtspinner import WaitingSpinner

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SCPSettingsWindow import SCPSettingsWindow
from GrepWindow import GrepWindow
from Nyxquery import Nyxquery
from TableView import TableView
from TableModel import TableModel
from utils import getSiteIps, getSites, make_combo_box_searchable, openSSH, openCSSH, filterIps, read_json, doSCP
from HotkeyWindow import HotkeyWindow

MAIN_TABLE_HEADER = ["Ip", "Name"]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        menu = self.menuBar()

        scpConfigButtonAction = QAction("SCP settings", self)
        scpConfigButtonAction.triggered.connect(self.openSCPSettingsWindow)

        file_menu = menu.addMenu("File")
        file_menu.addAction(scpConfigButtonAction)

        layout = QVBoxLayout()

        combo = QtWidgets.QComboBox()
        self.sites = getSites()
        self.site = self.sites[0]
        combo.addItems(self.sites)
        make_combo_box_searchable(combo)
        combo.currentIndexChanged.connect(self.siteComboChanged)

        upperLayout = QHBoxLayout()
        upperLayout.addWidget(combo, 50)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.textChanged.connect(self.filterMachines)

        upperLayout.addWidget(self.lineEdit, 50)

        upperWidget = QtWidgets.QWidget()
        upperWidget.setLayout(upperLayout)

        layout.addWidget(upperWidget)

        self.data = getSiteIps(self.site)
        self.wholeData = self.data

        self.table = TableView(self.startParallelSession)

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

        self.spinner = WaitingSpinner(self, True, True)

        layout.addWidget(self.table)
        layout.addWidget(self.spinner)

        lowerLayout = QHBoxLayout()

        grepButton = QtWidgets.QPushButton("Grep")
        grepButton.clicked.connect(self.openGrepWindow)

        hotkeysButton = QtWidgets.QPushButton("Hotkeys")
        hotkeysButton.clicked.connect(self.openHotkeyWindow)

        newPSButton = QtWidgets.QPushButton("New PS")
        # newPSButton.clicked.connect(self.startParallelSession)
        newPSButton.clicked.connect(lambda: self.startParallelSession())

        lowerLayout.addWidget(grepButton)
        lowerLayout.addWidget(hotkeysButton)
        lowerLayout.addWidget(newPSButton)

        lowerWidget = QtWidgets.QWidget()
        lowerWidget.setLayout(lowerLayout)
        layout.addWidget(lowerWidget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.adjustWindowSize()

        self.nyxquery = Nyxquery()
        self.nyxquery.site_ips_fetched.connect(self.siteIpsLoaded)
        self.nyxquery.sites_fetched.connect(self.siteIpsLoaded)

        self.controller = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.onKeyPress)
        self.listener.start()

    def onKeyPress(self, event):
        try:
            if not hasattr(event, 'name') or (isinstance(event, keyboard.Key) and event.name[0] != "f"):
                return
            data = read_json()
            if data["scpConf"].get("hotkey", "").lower() == event.name.lower():
                doSCP(data["scpConf"], self.controller, self.site)
                return

            for hotkey in data["hotkeys"]:
                if str(hotkey[2]).lower() == event.name.lower() and hotkey[1]:
                    print(hotkey[2] + "pressed")
                    self.controller.press(keyboard.Key.backspace) # to remove the '~' that may be generated when pressing certain fn key
                    self.controller.release(keyboard.Key.backspace)
                    self.controller.type(hotkey[0])
        except Exception as e:
            print(f"error: {e}")

    def startSingleConnection(self, index: QModelIndex) -> None:
        ip = self.data[index.row()][0]
        openSSH(ip)

    def startParallelSession(self, selectedIndexes: list[QModelIndex] = []):
        selected = self.table.selectedIndexes() if len(selectedIndexes) == 0 else selectedIndexes

        if len(selected) > 0:
            if len(selected) > 1:
                openCSSH(list(set([self.data[index.row()][0] for index in selected])))
            else:  # len == 1
                openSSH(self.data[selected[0].row()][0])

    def openHotkeyWindow(self):
        self.w = HotkeyWindow()
        self.w.show()

    def openGrepWindow(self):
        self.grepWindow = GrepWindow()
        self.grepWindow.show()

    def openSCPSettingsWindow(self):
        self.scpWindow = SCPSettingsWindow()
        self.scpWindow.show()

    def siteComboChanged(self, index):
        self.spinner.start()
        print(self.sites[index])
        self.site = self.sites[index]

        if self.nyxquery.isRunning():
            print("Thread already running!")
            self.nyxquery.terminate()

        self.nyxquery.getSiteIps(self.site)
        self.lineEdit.setText("")

    def siteIpsLoaded(self, ips):
        self.spinner.stop()
        self.data = ips
        self.wholeData = self.data
        self.model = TableModel(self.data, MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def filterMachines(self, s):
        self.data = filterIps(self.wholeData, s)
        self.model = TableModel(self.data, MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def adjustWindowSize(self):
        width = self.table.verticalHeader().width() + self.table.horizontalHeader().length() + self.table.frameWidth() * 2 + 40
        height = self.table.horizontalHeader().height() + self.table.verticalHeader().length() + self.table.frameWidth() * 2 + 20
        # self.setMinimumSize(width, height if height < 920 else 920)
        self.resize(width+150, 920) #height if height < 920 else 920

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        for index in selected.indexes():
            print(f'Selected: row {index.row()}, column {index.column()}, value: {index.data()}')

        for index in deselected.indexes():
            print(f'Deselected: row {index.row()}, column {index.column()}, value: {index.data()}')

    def scp(self):
        cb = QApplication.clipboard()
        # print("Clipboard Text: ", cb.text(mode=cb.Clipboard))
        # print("Selection Text: ", cb.text(mode=cb.Selection))

    def closeEvent(self, event):
        # Unhook all key listeners when closing the window
        self.listener.stop()
        event.accept()

print("Starting LDOT2")
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
