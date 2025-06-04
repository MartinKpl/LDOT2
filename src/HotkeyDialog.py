from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QCheckBox, QComboBox, QHBoxLayout, QPushButton, QLabel


class HotkeyDialog(QDialog):
    def __init__(self, data, parent=None):
        super(HotkeyDialog, self).__init__(parent)
        self.setWindowTitle("Hotkey")

        self.line_edit = QLineEdit()
        self.line_edit.setText(data[0])

        self.check_box = QCheckBox()
        self.check_box.setChecked(data[1])
        self.combo_box = QComboBox()
        comboItems =["F"+str(n+1) for n in range(12)]
        comboItems.insert(0, "None")
        self.combo_box.addItems(comboItems)

        index = self.combo_box.findText(data[2])
        if index >= 0:
            self.combo_box.setCurrentIndex(index)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Text"))
        layout.addWidget(self.line_edit)
        layout.addWidget(QLabel("Active"))
        layout.addWidget(self.check_box)
        layout.addWidget(QLabel("Hotkey"))
        layout.addWidget(self.combo_box)

        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        button_box.addWidget(save_button)

        layout.addLayout(button_box)
        self.setLayout(layout)

    def getValues(self):
        return {
            "text": self.line_edit.text(),
            "active": self.check_box.isChecked(),
            "hotkey": self.combo_box.currentText()
        }