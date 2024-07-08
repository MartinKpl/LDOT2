from typing import List
from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, header: List[str] = []):
        super(TableModel, self).__init__()
        self._data = data
        self._header = header

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()] if len(self._data) and len(self._data[index.row()]) > 0 else 0

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0] if len(self._data) > 0 else 0)
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and len(self._header) == len(self._data[0]):
            return self._header[section]