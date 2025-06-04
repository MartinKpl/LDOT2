from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QCheckBox, QComboBox, QHBoxLayout, QPushButton, QLabel

from src.utils import Hotkey


class HotkeyDialog(QDialog):
    def __init__(self, hotkey:Hotkey, parent=None):
        super(HotkeyDialog, self).__init__(parent)
        self.setWindowTitle("Hotkey")

        self.line_edit = QLineEdit()
        self.line_edit.setText(hotkey["text"])

        self.activeCheckBox = QCheckBox()
        self.activeCheckBox.setChecked(hotkey["active"])

        self.combo_box = QComboBox()
        comboItems =["F"+str(n+1) for n in range(12)]
        comboItems.insert(0, "None")
        self.combo_box.addItems(comboItems)

        index = self.combo_box.findText(hotkey["hotkey"])
        if index >= 0:
            self.combo_box.setCurrentIndex(index)

        self.autoEnterCheckbox = QCheckBox()
        self.autoEnterCheckbox.setChecked(hotkey["autoEnter"])

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Text"))
        layout.addWidget(self.line_edit)
        layout.addWidget(QLabel("Active"))
        layout.addWidget(self.activeCheckBox)
        layout.addWidget(QLabel("Hotkey"))
        layout.addWidget(self.combo_box)
        layout.addWidget(QLabel("AutoEnter"))
        layout.addWidget(self.autoEnterCheckbox)

        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        button_box.addWidget(save_button)

        layout.addLayout(button_box)
        self.setLayout(layout)

    def getValues(self)->Hotkey:
        return {
            "text": self.line_edit.text(),
            "active": self.activeCheckBox.isChecked(),
            "hotkey": self.combo_box.currentText(),
            "autoEnter": self.autoEnterCheckbox.isChecked()
        }