from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView

class TableView(QTableView):
    def __init__(self, openPSFunc):
        super(TableView, self).__init__()
        self.openPSFunc = openPSFunc

    def keyPressEvent(self, event):
        # Check if the Enter key is pressed
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handleEnterKey()
        else:
            super(TableView, self).keyPressEvent(event)

    def handleEnterKey(self):
        selected_indexes = self.selectedIndexes()
        if selected_indexes:
            self.openPSFunc(selected_indexes)
