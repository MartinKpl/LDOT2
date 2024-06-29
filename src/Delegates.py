import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QStyledItemDelegate, QCheckBox, QComboBox, QHBoxLayout, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QVariant


class CheckBoxDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        checkbox = QCheckBox(parent)
        checkbox.setTristate(False)
        checkbox.stateChanged.connect(self.commitAndCloseEditor)
        return checkbox

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        if value:
            editor.setCheckState(Qt.Checked)
        else:
            editor.setCheckState(Qt.Unchecked)

    def setModelData(self, editor, model, index):
        if editor.checkState() == Qt.Checked:
            model.setData(index, True, Qt.EditRole)
        else:
            model.setData(index, False, Qt.EditRole)

    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, QCheckBox):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)
        self.items = items

    def createEditor(self, parent, option, index):
        combobox = QComboBox(parent)
        combobox.addItems(self.items)
        combobox.currentIndexChanged.connect(self.commitAndCloseEditor)
        return combobox

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        if value:
            editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, QComboBox):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)