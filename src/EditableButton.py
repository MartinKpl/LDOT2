from PyQt5.QtWidgets import  QWidget, QPushButton, QLineEdit, QHBoxLayout
from utils import read_json, write_json
class EditableButton(QWidget):
    def __init__(self, quickFilterIndex: int, onClickHandler, parent=None):
        super().__init__(parent)
        self.quickFilterIndex = quickFilterIndex
        self.onClickHandler = onClickHandler
        # Create button and line edit
        try:
            text = read_json()['quickFilters'][quickFilterIndex]
        except KeyError:
            text = ""

        self.button = QPushButton(text)
        self.line_edit = QLineEdit(text)

        # Make line edit hidden initially
        self.line_edit.setVisible(False)

        # Remove default button focus outline
        # self.button.setStyleSheet("border: 1px solid gray; border-right: none; padding: 5px;")
        # self.line_edit.setStyleSheet("border: 1px solid gray; padding: 3px;")

        # Connect events
        self.button.clicked.connect(self.handle_button_click)  # Normal click
        self.button.installEventFilter(self)  # Enable double-click detection
        self.line_edit.editingFinished.connect(self.handle_editing_finished)

        # Layout to stack button and line edit
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)

    def eventFilter(self, obj, event):
        """ Detects double-clicks on the button """
        if obj == self.button and event.type() == event.MouseButtonDblClick:
            self.switch_to_edit()
            return True
        return super().eventFilter(obj, event)

    def handle_button_click(self):
        """ Normal button click behavior (can be customized) """
        self.onClickHandler(self.button.text())

    def switch_to_edit(self):
        """ Switch button to edit mode on double-click """
        self.line_edit.setText(self.button.text())  # Sync text
        self.button.setVisible(False)
        self.line_edit.setVisible(True)
        self.line_edit.setFocus()

    def handle_editing_finished(self):
        """ Update button text and switch back to button mode """
        new_text = self.line_edit.text().strip()
        if new_text:
            self.button.setText(new_text)

        self.line_edit.setVisible(False)
        self.button.setVisible(True)

        data = read_json()
        if 'quickFilters' not in data:
            data['quickFilters'] = ["", "", ""]

        data['quickFilters'][self.quickFilterIndex] = new_text
        write_json(data)


    def text(self) -> str:
        return self.button.text()