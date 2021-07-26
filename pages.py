import json

from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QTabWidget, \
    QSizePolicy, QInputDialog

import requester
from requester import Difficulty


class SudokuApp(QWidget):
    def __init__(self, parent=None):
        super(SudokuApp, self).__init__(parent)
        # vars
        self.setWindowTitle("Sudoku")
        with open("stylesheet.txt") as f:
            self.setStyleSheet("".join(f.readlines()))
        # construct and add widgets
        self.construct()

    def construct(self):
        self.setLayout(QVBoxLayout())
        tab = QTabWidget(self)
        gamePage = Game()
        settingsPage = Settings()
        tab.addTab(gamePage, "Game")
        tab.addTab(settingsPage, "Settings")
        self.layout().addWidget(tab)


class Game(QWidget):
    def __init__(self, parent=None):
        super(Game, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setLayout(QHBoxLayout())
        self.board = Board()
        self.btnGenBoard = QPushButton("Generate board")
        self.btnGenBoard.setObjectName("rbtn")
        self.btnGenBoard.clicked.connect(self.onGenBoardBtnClick)
        self.btnValidate = QPushButton("Validate")
        self.btnValidate.setObjectName("rbtn")
        self.btnValidate.clicked.connect(self.onValidateClick)
        self.btnSaveBoard = QPushButton("Save Board As Puzzle")
        self.btnSaveBoard.clicked.connect(self.onSaveBoardClick)
        self.btnSaveBoard.setObjectName("rbtn")
        self.btnLoadBoard = QPushButton("Load Board")
        self.btnLoadBoard.setObjectName("rbtn")
        rlayout = QVBoxLayout()
        rlayout.setAlignment(Qt.AlignCenter)
        rlayout.addWidget(self.btnGenBoard)
        rlayout.addWidget(self.btnValidate)
        rlayout.addWidget(self.btnSaveBoard)
        rlayout.addWidget(self.btnLoadBoard)
        self.layout().addWidget(self.board)
        self.layout().addLayout(rlayout)

    def onValidateClick(self):
        print(f"Checking...")
        if self.board.isWin():
            print(f"Complete!")

    def onGenBoardBtnClick(self):
        self.sender().setEnabled(False)
        self.board.getData(Difficulty.MEDIUM)
        self.sender().setEnabled(True)

    def onSaveBoardClick(self):
        board_state = self.board.getBoardState()
        name, ok = QInputDialog().getText(self, "Save Current Board", "Save as:")
        if ok and name:
            with open(f"Puzzles/{name}", 'w') as f:
                f.write(str(board_state))


class Board(QWidget):
    def __init__(self):
        super(Board, self).__init__()
        self.setupVars()
        self.construct()

    def construct(self):
        self.btns: [[QPushButton]] = [[QPushButton() for _ in range(9)] for _ in range(9)]
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
                        self.btns[r * 3 + rr][c * 3 + cc] = btn
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
        self.lastClicked: QPushButton = None

    def clear(self):
        """Clears the board"""
        for row in self.btns:
            for btn in row:
                btn.setText("")
                btn.setEnabled(True)

    def getBoardState(self) -> [[int]]:
        """Returns the board as a 9x9 2d array with ints."""
        board_state: [[int]] = []
        for r in range(9):
            templist = []
            for c in range(9):
                templist.append(self.btns[r][c].text())
            board_state.append(templist)
        return board_state

    def getData(self, diff: Difficulty):
        """Sends a GET request to the online API. Does not handle the response."""
        req = QNetworkRequest(QUrl(requester.getUrl(diff)))
        self.nam.get(req)

    def handleResponse(self,  reply):
        """Processes the response from the API."""
        er = reply.error()
        if er == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            board = json.loads(str(bytes_string, 'utf-8'))["board"]
            self.clear()
            for r, row in enumerate(board):
                for c, val in enumerate(row):
                    if val != 0:
                        self.btns[r][c].setText(f"{val}")
                        self.btns[r][c].setEnabled(False)
        else:
            print("Error occurred: ", er)
            print(reply.errorString())

    def onClick(self):
        if self.lastClicked is not None:
            self.lastClicked.setStyleSheet("")
        self.sender().setStyleSheet("background-color: #cbcac8;")
        self.lastClicked = self.sender()

    def keyReleaseEvent(self, key_event: QtGui.QKeyEvent) -> None:
        """Handles key presses."""
        if self.lastClicked is not None and (key_event.text().isdigit() or key_event.key() == Qt.Key_Backspace):
            if key_event.key() == Qt.Key_Backspace:
                self.lastClicked.setText(f"")
            else:
                self.lastClicked.setText(f"{key_event.text()}")

    def isWin(self) -> bool:
        vals = [[btn.text() for btn in row] for row in self.btns]
        # Check rows
        for r, row in enumerate(vals):
            if len(set(row)) != 9:
                print(f"Failed row check: {r}")
                return False
        # Check columns
        for c in range(len(vals[0])):
            if len(set(vals[:, c])) != 9:
                print(f"Failed column check: {c}")
                return False
        # todo :: check for box uniqueness
        return True


class Settings(QWidget):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Settings"))
