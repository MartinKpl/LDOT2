from typing import List
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QVariant, QModelIndex

from src.utils import Hotkey

columnIndexToColumnNameMapper = {
    0: 'text', 1: 'active', 2: 'hotkey', 3: 'autoEnter'
}

class HotkeysTable(QtCore.QAbstractTableModel):
    def __init__(self, data: List[Hotkey], header: List[str] = []):
        super(HotkeysTable, self).__init__()
        self._data = data #[list(i.values()) for i in data]
        print(list(data[0].keys()))
        self._header = header

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if isinstance(self._data[index.row()][columnIndexToColumnNameMapper[index.column()]], bool):
                return QVariant()
            return str(self._data[index.row()][columnIndexToColumnNameMapper[index.column()]])
        if role == Qt.CheckStateRole and index.column() in (1, 3):  # Column 1 and 3 are checkboxes
            return Qt.Checked if self._data[index.row()][columnIndexToColumnNameMapper[index.column()]] else Qt.Unchecked
        if role == Qt.TextAlignmentRole:
            if index.column() != 0:
                return Qt.AlignHCenter + Qt.AlignVCenter

        return QVariant()

    def rowCount(self, parent: QModelIndex = ...):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0]) if len(self._data) > 0 else 0

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and len(self._data) > 0 and len(self._header) == len(self._data[0]):
            return self._header[section]

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled # | Qt.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][columnIndexToColumnNameMapper[index.column()]] = value
            return True

        return False

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        for _ in range(count):
            self._data.insert(row, {
                "text": "",
                "active": True,
                "hotkey": "",
                "autoEnter": False
            })
        self.endInsertRows()

        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        for _ in range(count):
            self._data.pop(row)
        self.endRemoveRows()

        return True

    def getModelData(self):
        return self._data
