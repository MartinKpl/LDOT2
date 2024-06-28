from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDataWidgetMapper, QDialog, QHBoxLayout, QPushButton

from HotkeysTable import HotkeysTable
from HotkeyDialog import HotkeyDialog


class HotkeyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotkeys")

        self.setMinimumSize(900, 500)
        self.resize(900, 500)

        layout = QVBoxLayout()

        self.table = QtWidgets.QTableView()

        data = [
            ["sudo su - apps", True, "F2"],
            ["sudo su - playtech", False, "F4"]
        ]

        self.model = HotkeysTable(data)
        self.table.setModel(self.model)

        # Make the table expand to fill the window
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.setCentralWidget(self.table)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        layout.addWidget(self.table)

        self.table.doubleClicked.connect(self.showEditDialog)

        buttonsLayout = QHBoxLayout()
        addHotkeyButton = QPushButton("Add Hotkey")
        modifyHotkeyButton = QPushButton("Modify Hotkey")
        deleteHotkeyButton = QPushButton("Delete Hotkey")

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
        dialog = HotkeyDialog(self)
        mapper = QDataWidgetMapper(dialog)
        mapper.setModel(self.model)
        mapper.addMapping(dialog.line_edit, 0)
        mapper.addMapping(dialog.check_box, 1, b"checked")
        mapper.addMapping(dialog.combo_box, 2)
        mapper.setCurrentModelIndex(index)

        dialog.resize(450, 250)

        dialog.exec_()
        # if dialog.exec_() == QDialog.Accepted:
            # self.model.setData(self.model.index(index.row(), 0), dialog.line_edit.text())
            # self.model.setData(self.model.index(index.row(), 1), dialog.check_box.isChecked())
            # self.model.setData(self.model.index(index.row(), 2), dialog.combo_box.currentText())