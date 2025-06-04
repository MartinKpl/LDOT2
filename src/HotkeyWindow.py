from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDataWidgetMapper, QDialog, QHBoxLayout, QPushButton

from HotkeysTable import HotkeysTable
from HotkeyDialog import HotkeyDialog
from utils import read_json, write_json


class HotkeyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotkeys")

        self.setMinimumSize(900, 500)
        self.resize(900, 500)

        layout = QVBoxLayout()

        self.table = QtWidgets.QTableView()

        self.data = read_json()["hotkeys"]

        self.model = HotkeysTable(self.data, ["Command", "Active", "Hotkey"])
        self.table.setModel(self.model)

        # Make the table expand to fill the window
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.setCentralWidget(self.table)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table.doubleClicked.connect(self.showEditDialog)

        layout.addWidget(self.table)

        buttonsLayout = QHBoxLayout()
        addHotkeyButton = QPushButton("Add Hotkey")
        modifyHotkeyButton = QPushButton("Modify Hotkey")
        deleteHotkeyButton = QPushButton("Delete Hotkey")

        addHotkeyButton.clicked.connect(self.showNewHotkeyDialog)
        deleteHotkeyButton.clicked.connect(self.deleteNewHotkey)

        buttonsLayout.addWidget(addHotkeyButton)
        buttonsLayout.addWidget(modifyHotkeyButton)
        buttonsLayout.addWidget(deleteHotkeyButton)

        buttonsLayoutWidget = QWidget()
        buttonsLayoutWidget.setLayout(buttonsLayout)

        layout.addWidget(buttonsLayoutWidget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def showEditDialog(self, index):
        row = index.row()
        row_data = [
            self.data[row][0],  # Text column
            self.data[row][1],  # Checkbox column
            self.data[row][2]   # Combo column
        ]

        print(row_data)

        dialog = HotkeyDialog(row_data, self)

        dialog.resize(450, 250)

        if dialog.exec_() == dialog.Accepted:
            newValues = dialog.getValues()
            self.model.setData(self.model.index(row, 0), newValues['text'], Qt.EditRole)
            self.model.setData(self.model.index(row, 1), newValues['active'], Qt.EditRole)
            self.model.setData(self.model.index(row, 2), newValues['hotkey'], Qt.EditRole)


    def showNewHotkeyDialog(self):
        dialog = HotkeyDialog(self)

        dialog.resize(450, 250)

        # dialog.exec_()
        self.model.insertRows(self.model.rowCount(), 1)
        if dialog.exec_() == QDialog.Accepted:
            lastIndex = len(self.data) - 1
            self.model.setData(self.model.index(lastIndex, 0), dialog.line_edit.text(), Qt.EditRole)
            self.model.setData(self.model.index(lastIndex, 1), dialog.check_box.isChecked(), Qt.EditRole)
            self.model.setData(self.model.index(lastIndex, 2), dialog.combo_box.currentText(), Qt.EditRole)

    def deleteNewHotkey(self):
        selectedRowsIndexes = sorted(set(index.row() for index in self.table.selectionModel().selectedIndexes()), reverse=True)
        print(selectedRowsIndexes)
        for index in selectedRowsIndexes:
            self.model.removeRow(index)

    def closeEvent(self, event):
        hotkeys = self.model.getModelData()
        data = read_json()
        data["hotkeys"] = hotkeys
        write_json(data)
        QMainWindow.closeEvent(self, event)
