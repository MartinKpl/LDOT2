import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from TableModel import TableModel

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()

        data = [
          [4, 9, 2],
          [1, 0, 0],
          [3, 5, 0],
          [3, 3, 2],
          [7, 8, 9],
        ]

        self.model = TableModel(data, ["first", "second", "third"])
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)

        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table.selectionModel().selectionChanged.connect(self.selectionChanged)
        # self.table.resizeColumnsToContents()
        # self.table.resizeRowsToContents()

        self.adjustSize()
    
    def selectionChanged(self, selected, deselected):
        print("Selected: ", selected)
        print("Deselected: ", deselected)


app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec_()