from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QCheckBox, QComboBox, QHBoxLayout, QPushButton, QLabel


class HotkeyDialog(QDialog):
    def __init__(self, parent=None):
        super(HotkeyDialog, self).__init__(parent)
        self.setWindowTitle("Hotkey")

        self.line_edit = QLineEdit()
        self.check_box = QCheckBox()
        self.combo_box = QComboBox()
        comboItems =["F"+str(n+1) for n in range(12)]
        comboItems.insert(0, "None")
        self.combo_box.addItems(comboItems)

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