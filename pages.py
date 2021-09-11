import json
import os
from os import listdir
from os.path import join, isfile

from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QTabWidget, \
    QSizePolicy, QInputDialog, QDialog, QScrollArea, QListWidget, QListWidgetItem

import requester
from OtherWidgets import StopwatchWidget
from requester import Difficulty


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


class Game(QWidget):
    def __init__(self, parent=None):
        super(Game, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setLayout(QHBoxLayout())
        self.board = Board()
        self.stopwatch = StopwatchWidget()
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
            self.board.getData(self.diffSelector.getDifficultySelected())
        self.sender().setEnabled(True)

    @pyqtSlot()
    def onSaveBoardClick(self):
        board_state = self.board.getBoardState()
        name, ok = QInputDialog().getText(self, "Save Current Board", "Save as:")
        if ok and name:
            with open(f"Puzzles/{name}", 'w') as f:
                f.write(json.dumps(board_state))

    @pyqtSlot()
    def onLoadBoardClick(self):
        # Get user to select from list
        dg = PuzzleSelector(self)
        if dg.exec_() == QDialog.Accepted:
            text = dg.getSelectedText()
            self.board.loadBoardState(text)


class Board(QWidget):
    data_received = pyqtSignal()

    def __init__(self):
        super(Board, self).__init__()
        self.setupVars()
        self.construct()

    def construct(self):
        self.buttons: [[QPushButton]] = [[QPushButton() for _ in range(9)] for _ in range(9)]
        self.setLayout(QGridLayout())
        self.layout().setSpacing(4)
        sp = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # sp.setHeightForWidth(True)
        for r in range(3):
            for c in range(3):
                frame: QFrame = QFrame()
                frame.setLayout(QGridLayout())
                frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
                frame.layout().setSpacing(2)
                frame.layout().setContentsMargins(0, 0, 0, 0)
                # Create inner
                for rr in range(3):
                    for cc in range(3):
                        btn = QPushButton()
                        self.buttons[r * 3 + rr][c * 3 + cc] = btn
                        btn.setMinimumSize(75, 75)
                        btn.setObjectName("board")
                        btn.setSizePolicy(sp)
                        btn.clicked.connect(self.onClick)
                        frame.layout().addWidget(btn, rr, cc)
                self.layout().addWidget(frame, r, c)
        # eof

    def setupVars(self):
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        self.last_clicked: QPushButton = QPushButton()

    def clear(self):
        """Clears the board"""
        for row in self.buttons:
            for btn in row:
                btn.setText("")
                btn.setEnabled(True)

    def getBoardState(self) -> [[int]]:
        """Returns the board as a 9x9 2d array with ints."""
        board_state: [[int]] = []
        for r in range(9):
            temp_list = []
            for c in range(9):
                temp_list.append(self.buttons[r][c].text())
            board_state.append(temp_list)
        return board_state

    def loadBoardState(self, file_name: str):
        try:
            with open(f"Puzzles/{file_name}") as f:
                board = json.loads(f.readlines()[0])
                self.clear()
                for r in range(9):
                    for c in range(9):
                        if board[r][c] != "":
                            self.buttons[r][c].setText(board[r][c])
                            self.buttons[r][c].setEnabled(False)
        except Exception as e:
            print(f"Error Loading Board: {e}")

    def getData(self, diff: Difficulty):
        """Sends a GET request to the online API. Does not handle the response."""
        req = QNetworkRequest(QUrl(requester.getUrl(diff)))
        self.nam.get(req)

    @pyqtSlot(QNetworkReply)
    def handleResponse(self, reply: QNetworkReply):
        """Processes the response from the API."""
        er = reply.error()
        if er == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            board = json.loads(str(bytes_string, 'utf-8'))["board"]
            self.clear()
            for r, row in enumerate(board):
                for c, val in enumerate(row):
                    if val != 0:
                        self.buttons[r][c].setText(f"{val}")
                        self.buttons[r][c].setEnabled(False)
            self.data_received.emit()
        else:
            print("Error occurred: ", er)
            print(reply.errorString())

    @pyqtSlot()
    def onClick(self):
        if self.last_clicked is not None:
            self.last_clicked.setStyleSheet("")
        self.sender().setStyleSheet("background-color: #cbcac8;")
        self.last_clicked = self.sender()

    @pyqtSlot(QtGui.QKeyEvent)
    def keyReleaseEvent(self, key_event: QtGui.QKeyEvent) -> None:
        """Handles key presses."""
        if self.last_clicked is not None and (key_event.text().isdigit() or key_event.key() == Qt.Key_Backspace):
            if key_event.key() == Qt.Key_Backspace:
                self.last_clicked.setText(f"")
            else:
                self.last_clicked.setText(f"{key_event.text()}")

    def isWin(self) -> bool:
        values = [[btn.text() for btn in row] for row in self.buttons]
        # Check rows
        for r, row in enumerate(values):
            if (len(set(row)) != 9) or ("" in row):
                print(f"Failed row check: {r}")
                return False
        # Check columns
        for c in range(len(values[0])):
            col = self.column(values, c)
            if (len(set(col)) != 9) or ("" in col):
                print(f"Failed column check: {c}")
                return False
        for r in range(3):
            for c in range(3):
                temp_set = set()
                for rr in range(3):
                    for cc in range(3):
                        temp_set.add(self.buttons[r * 3 + rr][c * 3 + cc].text())
                if ("" in temp_set) or (len(temp_set) != 9):
                    print(f"Failed box check: {r=} {c=}")
                    return False
        return True

    @staticmethod
    def column(matrix, i):
        return [row[i] for row in matrix]


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
        cur_dir = os.path.join(os.getcwd(), "Puzzles")
        file_names = [f for f in listdir(cur_dir) if isfile(join(cur_dir, f))]
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


class Settings(QWidget):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Settings"))
