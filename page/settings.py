from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class Settings(QWidget):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Settings"))
