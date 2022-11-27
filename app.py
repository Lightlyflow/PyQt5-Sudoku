from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from page.pages import Game, Settings


class SudokuApp(QWidget):
    def __init__(self, parent=None):
        super(SudokuApp, self).__init__(parent)
        # vars
        self.setWindowTitle("Sudoku")
        self.setWindowIcon(QtGui.QIcon("res/icon.png"))
        with open("stylesheet.txt") as f:
            self.setStyleSheet("".join(f.readlines()))
        # construct and add widgets
        self.construct()

    def construct(self):
        self.setLayout(QVBoxLayout())
        tab = QTabWidget(self)
        game_page = Game()
        settings_page = Settings()
        tab.addTab(game_page, "Game")
        tab.addTab(settings_page, "Settings")
        self.layout().addWidget(tab)
