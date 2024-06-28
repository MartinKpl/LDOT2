from typing import List
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QVariant


class HotkeysTable(QtCore.QAbstractTableModel):
    def __init__(self, data, header: List[str] = []):
        super(HotkeysTable, self).__init__()
        self._data = data
        self._header = header

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if isinstance(self._data[index.row()][index.column()], bool):
                return QVariant()
            return str(self._data[index.row()][index.column()])
        if role == Qt.CheckStateRole and index.column() == 1:  # Assuming column 1 is for checkboxes
            return Qt.Checked if self._data[index.row()][index.column()] else Qt.Unchecked
        if role == Qt.TextAlignmentRole:
            if index.column() != 0:
                return Qt.AlignHCenter

        return QVariant()

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and len(self._header) == len(self._data[0]):
            return self._header[section]

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled


    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True