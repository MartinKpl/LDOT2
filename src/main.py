import sys, os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QItemSelection, QModelIndex, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication, QToolBar, QAction, QMessageBox, QPushButton
from pynput import keyboard
from pyqtspinner import WaitingSpinner

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SCPSettingsWindow import SCPSettingsWindow
from GrepWindow import GrepWindow
from Nyxquery import Nyxquery
from TableView import TableView
from TableModel import TableModel
from utils import getSiteIps, getSites, make_combo_box_searchable, openSSH, openCSSH, filterIps, read_json, doSCP, filterIpsByRole
from HotkeyWindow import HotkeyWindow
from EditableButton import EditableButton

MAIN_TABLE_HEADER = ["Ip", "Name"]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        menu = self.menuBar()

        scpConfigButtonAction = QAction("SCP settings", self)
        scpConfigButtonAction.triggered.connect(self.openSCPSettingsWindow)

        file_menu = menu.addMenu("File")
        file_menu.addAction(scpConfigButtonAction)

        self.nyxquery = Nyxquery()
        self.nyxquery.site_ips_fetched.connect(self.siteIpsLoaded)
        self.nyxquery.sites_fetched.connect(self.sitesLoaded)
        self.nyxquery.roles_fetched.connect(self.rolesLoaded)

        layout = QVBoxLayout()

        self.combo = QtWidgets.QComboBox()
        self.sites = [""]#getSites()
        self.site = self.sites[0]
        self.combo.addItems(self.sites)
        make_combo_box_searchable(self.combo)
        self.combo.currentIndexChanged.connect(self.siteComboChanged)

        headerLayout = QVBoxLayout()
        upperLayout = QHBoxLayout()
        upperLayout.addWidget(self.combo, 50)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setFocusPolicy(Qt.StrongFocus)
        self.lineEdit.textChanged.connect(self.filterMachines)

        self.rolesCombo = QtWidgets.QComboBox()
        self.roles = [""]
        self.role = self.roles[0]
        self.rolesCombo.addItems(self.roles)
        make_combo_box_searchable(self.rolesCombo)
        self.rolesCombo.currentIndexChanged.connect(self.filterMachinesByRoles)

        rightUpperLayout = QVBoxLayout()

        rightUpperLayout.addWidget(self.lineEdit)
        rightUpperLayout.addWidget(self.rolesCombo)
        upperLayout.addLayout(rightUpperLayout, 50)

        headerLayout.addLayout(upperLayout)

        bottomLayout = QHBoxLayout()

        self.editableButton1 = EditableButton(0, self.filterMachinesFromEditableButton)
        self.editableButton2 = EditableButton(1, self.filterMachinesFromEditableButton)
        self.editableButton3 = EditableButton(2, self.filterMachinesFromEditableButton)

        bottomLayout.addWidget(self.editableButton1)
        bottomLayout.addWidget(self.editableButton2)
        bottomLayout.addWidget(self.editableButton3)

        bottomLayout.setSpacing(0)
        bottomLayout.setContentsMargins(0,0,0,0)

        headerLayout.addLayout(bottomLayout)

        headerWidget = QtWidgets.QWidget()
        headerWidget.setLayout(headerLayout)

        layout.addWidget(headerWidget)

        self.data = [["", ""]]#getSiteIps(self.site)
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

        addSSH = QtWidgets.QPushButton("Add SSH")
        addSSH.clicked.connect(self.addSSH)

        grepButton = QtWidgets.QPushButton("Grep")
        grepButton.clicked.connect(self.openGrepWindow)

        hotkeysButton = QtWidgets.QPushButton("Hotkeys")
        hotkeysButton.clicked.connect(self.openHotkeyWindow)

        newPSButton = QtWidgets.QPushButton("New PS")
        # newPSButton.clicked.connect(self.startParallelSession)
        newPSButton.clicked.connect(lambda: self.startParallelSession())

        lowerLayout.addWidget(addSSH)
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

        self.controller = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.onKeyPress)
        self.listener.start()
        self.loadSites()

    def onKeyPress(self, event):
        try:
            if not hasattr(event, 'name') or (isinstance(event, keyboard.Key) and event.name[0] != "f"):
                return
            data = read_json()
            if "scpConf" in data and data["scpConf"].get("hotkey", "").lower() == event.name.lower():
                doSCP(data["scpConf"], self.controller, self.site)
                return

            for hotkey in data["hotkeys"]:
                if str(hotkey["hotkey"]).lower() == event.name.lower() and hotkey["active"]:
                    print(hotkey["hotkey"] + " pressed")
                    self.controller.press(keyboard.Key.backspace) # to remove the '~' that may be generated when pressing certain fn key
                    self.controller.release(keyboard.Key.backspace)

                    text = hotkey["text"].replace("{{paste}}", self.getClipboardText())

                    self.controller.type(text)

                    if hotkey["autoEnter"]:
                        self.controller.press(keyboard.Key.enter)
                        self.controller.release(keyboard.Key.enter)
        except Exception as e:
            print(f"error: {e}")

    def getClipboardText(self):
        cb = QApplication.clipboard()
        filename = cb.text(mode=cb.Selection)
        if filename == "":
            filename = cb.text(mode=cb.Clipboard)

        return filename

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

    def addSSH(self):
        data = read_json()
        rsaPath = data["scpConf"].get("rsaPath")
        if rsaPath is None or rsaPath == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("No RSA key set")
            msg.setInformativeText('No RSA key file path has been set. To do so, set it up in File->SCP Settings->RSA file')
            msg.setWindowTitle("Error")
            msg.setMinimumSize(600,200)
            msg.exec_()
        else:
            os.system(f"gnome-terminal -- bash -c 'ssh-add {rsaPath}'")

    def openSCPSettingsWindow(self):
        self.scpWindow = SCPSettingsWindow()
        self.scpWindow.show()

    def siteComboChanged(self, index):
        self.startSpinner()
        print(self.sites[index])
        self.site = self.sites[index]

        if self.nyxquery.isRunning():
            print("Thread already running! Waiting to get site's IPs")
            self.nyxquery.quit()
            self.nyxquery.wait()

        self.nyxquery.getSiteIps(self.site)
        self.lineEdit.setText("")

    def filterMachinesByRoles(self, index):
        if index < 0:
            return
        self.data = filterIpsByRole(self.wholeData, self.roles[index])
        self.model = TableModel(self.data, MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def siteIpsLoaded(self, ips):
        if self.nyxquery.isRunning():
            self.nyxquery.quit()
            self.nyxquery.wait()
        self.spinner.stop()
        self.data = ips
        self.wholeData = self.data
        self.model = TableModel(self.data, MAIN_TABLE_HEADER)
        self.table.setModel(self.model)
        QtCore.QTimer.singleShot(0, self.lineEdit.setFocus)

    def loadSites(self):
        self.startSpinner()

        if self.nyxquery.isRunning():
            print("Thread already running! Waiting to get sites")
            self.nyxquery.quit()
            self.nyxquery.wait()

        self.nyxquery.getSites()
        self.lineEdit.setText("")

    def sitesLoaded(self, sites):
        self.spinner.stop()
        self.sites = sites
        self.site = self.sites[0]
        self.combo.clear()
        self.combo.addItems(self.sites)
        # self.nyxquery.exit()
        # self.combo.setCurrentIndex(0)

        # self.siteComboChanged(0)
        self.loadRoles()


    def loadRoles(self):
        self.startSpinner()

        if self.nyxquery.isRunning():
            print("Thread already running! Waiting to get roles")
            self.nyxquery.quit()
            self.nyxquery.wait()

        self.nyxquery.getRoles()

    def rolesLoaded(self, roles):
        self.spinner.stop()
        self.roles = roles
        self.role = self.roles[0]
        self.rolesCombo.clear()
        self.rolesCombo.addItems(self.roles)
        self.nyxquery.exit()

    def filterMachinesFromEditableButton(self, s):
        self.lineEdit.setText(s)
        self.filterMachines(s)

    def filterMachines(self, s):
        self.data = filterIps(self.wholeData, s)
        self.model = TableModel(self.data, MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def adjustWindowSize(self):
        # width = self.table.verticalHeader().width() + self.table.horizontalHeader().length() + self.table.frameWidth() * 2 + 40
        # height = self.table.horizontalHeader().height() + self.table.verticalHeader().length() + self.table.frameWidth() * 2 + 20
        # self.setMinimumSize(width, height if height < 920 else 920)
        self.resize(480, 920) #height if height < 920 else 920

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        for index in selected.indexes():
            print(f'Selected: row {index.row()}, column {index.column()}, value: {index.data()}')

        for index in deselected.indexes():
            print(f'Deselected: row {index.row()}, column {index.column()}, value: {index.data()}')

    def closeEvent(self, event):
        # Unhook all key listeners when closing the window
        self.listener.stop()
        event.accept()

    def startSpinner(self):
        if not self.spinner.is_spinning:
            self.spinner.start()

print("Starting LDOT2")
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
