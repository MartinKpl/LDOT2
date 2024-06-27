import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QItemSelection
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TableModel import TableModel
from utils import getSiteIps, getSites, make_combo_box_searchable


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()

        layout = QVBoxLayout()

        combo = QtWidgets.QComboBox()
        self.sites = getSites()
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

        data = getSiteIps("")

        self.model = TableModel(data, ["Code", "IP", "Name"])
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)

        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table.selectionModel().selectionChanged.connect(self.selectionChanged)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        layout.addWidget(self.table)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.adjustWindowSize()

    def siteComboChanged(self, index):
        print(self.sites[index])

    def filterMachines(self, s):
        self.model = TableModel(getSiteIps("", s), ["Code", "Ip", "Name"])
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