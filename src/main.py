import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QItemSelection, QModelIndex
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TableModel import TableModel
from utils import getSiteIps, getSites, make_combo_box_searchable, openSSH, openCSSH
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
        self.model = TableModel(getSiteIps(self.site), MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def filterMachines(self, s):
        self.model = TableModel(getSiteIps(self.site, s), MAIN_TABLE_HEADER)
        self.table.setModel(self.model)

    def adjustWindowSize(self):
        width = self.table.verticalHeader().width() + self.table.horizontalHeader().length() + self.table.frameWidth() * 2 + 40
        height = self.table.horizontalHeader().height() + self.table.verticalHeader().length() + self.table.frameWidth() * 2 + 20
        self.setMinimumSize(width, height if height < 920 else 920)
        self.resize(width+150, height if height < 920 else 920)

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        for index in selected.indexes():
            print(f'Selected: row {index.row()}, column {index.column()}, value: {index.data()}')

        for index in deselected.indexes():
            print(f'Deselected: row {index.row()}, column {index.column()}, value: {index.data()}')


app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec_()