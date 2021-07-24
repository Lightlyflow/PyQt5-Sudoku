import json

from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QTabWidget, \
    QSizePolicy

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
        self.btnGenBoard.setObjectName("generate")
        self.btnGenBoard.clicked.connect(self.onGenBoardBtnClick)
        self.btnValidate = QPushButton("Validate")
        self.btnValidate.setObjectName("validate")
        rlayout = QVBoxLayout()
        rlayout.setAlignment(Qt.AlignCenter)
        rlayout.addWidget(self.btnGenBoard)
        rlayout.addWidget(self.btnValidate)
        self.layout().addWidget(self.board)
        self.layout().addLayout(rlayout)

    def onGenBoardBtnClick(self):
        self.sender().setEnabled(False)
        self.board.getData(Difficulty.MEDIUM)
        self.sender().setEnabled(True)


class Board(QWidget):
    def __init__(self):
        super(Board, self).__init__()
        self.setupVars()
        self.construct()

    def construct(self):
        self.btns = [[0 for _ in range(9)] for _ in range(9)]
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

    def clear(self):
        for row in self.btns:
            for btn in row:
                btn.setText("")
                btn.setEnabled(True)

    def setupVars(self):
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        self.lastClicked: QPushButton = None

    def getData(self, diff: Difficulty):
        req = QNetworkRequest(QUrl(requester.getUrl(diff)))
        self.nam.get(req)

    def handleResponse(self, reply):
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
        if self.isWin():
            print("Winner!")

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if self.lastClicked is not None and (event.text().isdigit()):
            self.lastClicked.setText(f"{event.text()}")

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print(f"Closing...")

    def isWin(self) -> bool:
        vals = [[btn.text() for btn in row] for row in self.btns]
        intvals = [[0 for _ in range(9)] for _ in range(9)]
        # Check if all lbls are nums
        for r, row in enumerate(vals):
            for c, val in enumerate(row):
                if val == "":
                    return False
                intvals[r][c] = int(val)
        # Check rows
        for r, row in enumerate(vals):
            if len(set(row)) != 9:
                return False
        # Check columns
        for c in range(len(vals[0])):
            if len(set(vals[:, c])) != 9:
                return False
        return True


class Settings(QWidget):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.construct()

    def construct(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Settings"))
