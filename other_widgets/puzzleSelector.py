from os import getcwd, path, listdir

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QListWidget, QPushButton, QListWidgetItem


class PuzzleSelector(QDialog):
    def __init__(self, parent=None):
        super(PuzzleSelector, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setObjectName("selectPuzzle")
        self.setLayout(QVBoxLayout())
        self.scroll_area = QScrollArea()
        self.puzzle_list = QListWidget()
        self.ok_btn = QPushButton("Select")
        cur_dir = path.join(getcwd(), "../Puzzles")
        file_names = [f for f in listdir(cur_dir) if path.isfile(path.join(cur_dir, f))]
        for name in file_names:
            QListWidgetItem(f"{name}", self.puzzle_list)
        self.scroll_area.setWidget(self.puzzle_list)
        self.layout().addWidget(self.scroll_area)
        self.layout().addWidget(self.ok_btn)
        self.ok_btn.clicked.connect(self.onOkBtnClicked)

    @pyqtSlot()
    def onOkBtnClicked(self):
        if len(self.puzzle_list.selectedItems()) == 1:
            self.accept()

    def getSelectedText(self) -> str:
        return self.puzzle_list.selectedItems()[0].text()

