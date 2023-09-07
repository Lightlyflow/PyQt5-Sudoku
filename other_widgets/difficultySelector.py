from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QListWidgetItem, QPushButton, QWidget

from data_manager import Difficulty


class DifficultySelector(QDialog):
    def __init__(self, parent=None):
        super(DifficultySelector, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setObjectName("diffSelector")
        # widget stuff
        self.setLayout(QVBoxLayout())
        self.list_diffs = QListWidget()
        self.bottom_layout = QHBoxLayout()
        self.diffEasy = QListWidgetItem("Easy", self.list_diffs)
        self.diffMedium = QListWidgetItem("Medium", self.list_diffs)
        self.diffHard = QListWidgetItem("Hard", self.list_diffs)
        self.diffRandom = QListWidgetItem("Random", self.list_diffs)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_ok = QPushButton("Ok")
        self.bot_container = QWidget()
        self.bottom_layout.addWidget(self.btn_cancel)
        self.bottom_layout.addWidget(self.btn_ok)
        self.bot_container.setLayout(self.bottom_layout)
        self.layout().addWidget(self.list_diffs)
        self.layout().addWidget(self.bot_container)
        # Adding func
        self.btn_cancel.clicked.connect(self.onBtnCancel)
        self.btn_ok.clicked.connect(self.onBtnOk)

    def onBtnCancel(self):
        self.reject()

    def onBtnOk(self):
        self.accept()

    def getDifficultySelected(self):
        return {"Easy": Difficulty.EASY,
                "Medium": Difficulty.MEDIUM,
                "Hard": Difficulty.HARD,
                "Random": Difficulty.RANDOM}.get(self.list_diffs.selectedItems()[0].text())
