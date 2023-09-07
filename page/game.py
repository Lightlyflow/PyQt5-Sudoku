from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QInputDialog, QDialog

from other_widgets import CStopwatch
from other_widgets.difficultySelector import DifficultySelector
from other_widgets.gameBoard import Board
from other_widgets.puzzleSelector import PuzzleSelector
from page.pages import savesManager


class Game(QWidget):
    def __init__(self, parent=None):
        super(Game, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setLayout(QHBoxLayout())
        self.board = Board()
        self.stopwatch = CStopwatch()
        self.btnGenBoard = QPushButton("Generate board")
        self.btnGenBoard.setObjectName("rbtn")
        self.btnValidate = QPushButton("Validate")
        self.btnValidate.setObjectName("rbtn")
        self.btnSaveBoard = QPushButton("Save Board As Puzzle")
        self.btnSaveBoard.setObjectName("rbtn")
        self.btnLoadBoard = QPushButton("Load Board")
        self.btnLoadBoard.setObjectName("rbtn")
        # Other widgets
        self.diffSelector = DifficultySelector(self)
        # adding functionality
        self.btnGenBoard.clicked.connect(self.onGenBoardBtnClick)
        self.btnValidate.clicked.connect(self.onValidateClick)
        self.btnSaveBoard.clicked.connect(self.onSaveBoardClick)
        self.btnLoadBoard.clicked.connect(self.onLoadBoardClick)
        self.board.data_received.connect(lambda: self.stopwatch.start())
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.stopwatch)
        right_layout.addWidget(self.btnGenBoard)
        right_layout.addWidget(self.btnValidate)
        right_layout.addWidget(self.btnSaveBoard)
        right_layout.addWidget(self.btnLoadBoard)
        self.layout().addWidget(self.board)
        self.layout().addLayout(right_layout)

    @pyqtSlot()
    def onValidateClick(self):
        print(f"Checking...")
        if self.board.isWin():
            self.stopwatch.stop()
            print(f"Complete!")

    @pyqtSlot()
    def onGenBoardBtnClick(self):
        self.sender().setEnabled(False)
        if self.diffSelector.exec_() == QDialog.Accepted:
            self.board.getNewBoardData(self.diffSelector.getDifficultySelected())
        self.sender().setEnabled(True)

    @pyqtSlot()
    def onSaveBoardClick(self):
        name, ok = QInputDialog().getText(self, "Save Current Board", "Save as:")
        if ok and name:
            savesManager.data['time'] = self.stopwatch.getTime()
            savesManager.data['board'] = self.board.getBoardState()
            savesManager.data['frozen'] = self.board.getStaticBoard()
            print(f"{savesManager.data['frozen'] = }")
            savesManager.save(name)

    @pyqtSlot()
    def onLoadBoardClick(self):
        # todo :: load time
        # Get user to select from list
        dg = PuzzleSelector(self)
        if dg.exec_() == QDialog.Accepted:
            fileName = dg.getSelectedText()
            savesManager.load_data(fileName)
            self.board.loadBoardState(fileName)
            # fixme :: Load time
            h, m, s = list(map(int, savesManager.data['time'].split(":")))
            self.stopwatch.setTime(h, m, s)