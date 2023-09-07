import json

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QUrl, pyqtSlot, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QSizePolicy, QFrame

# TODO :: Fix saves manager access (shouldn't be global)
from data_manager import Difficulty, path_gen
from page.pages import savesManager


class Board(QWidget):
    data_received = pyqtSignal()

    def __init__(self):
        super(Board, self).__init__()
        self.setupVars()
        self.construct()

    def construct(self):
        # Data
        self.buttons: [[QPushButton]] = [[QPushButton() for _ in range(9)] for _ in range(9)]
        self.static_board = None
        # GUI vars
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
        """Clears the board visually and enables all buttons."""
        for row in self.buttons:
            for btn in row:
                btn.setText("")
                btn.setEnabled(True)

    def getBoardState(self) -> [[str]]:
        """Returns the board as a 9x9 2d array with ints."""
        board_state = []
        for r in range(9):
            temp_list = []
            for c in range(9):
                temp_list.append(self.buttons[r][c].text())
            board_state.append(temp_list)
        return board_state

    def getStaticBoard(self) -> [[str]]:
        frozen = []
        for r in range(9):
            tmp_row = []
            for c in range(9):
                if not self.buttons[r][c].isEnabled():
                    tmp_row.append(self.buttons[r][c].text())
                else:
                    tmp_row.append("")
            frozen.append(tmp_row)
        return frozen

    def loadBoardState(self, file_name: str):
        """Loads the board state visually."""
        try:
            self.clear()
            # load frozen board
            for r, row in enumerate(savesManager.data['frozen']):
                for c, val in enumerate(row):
                    if val != "":
                        self.buttons[r][c].setText(val)
                        self.buttons[r][c].setEnabled(False)
            # load editable board
            for r, row in enumerate(savesManager.data['board']):
                for c, val in enumerate(row):
                    self.buttons[r][c].setText(val)
        except Exception as e:
            print(f"Error Loading Board: \n{e}")

    def getNewBoardData(self, diff: Difficulty):
        """Sends a GET request to the online API. Does not handle the response."""
        reqBoard = QNetworkRequest(QUrl(path_gen.getUrl(diff)))
        self.nam.get(reqBoard)

    @pyqtSlot(QNetworkReply)
    def handleResponse(self, reply: QNetworkReply):
        """Processes the response from the API."""
        er = reply.error()
        if er == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            board = json.loads(str(bytes_string, 'utf-8'))["board"]
            self.static_board = eval(json.dumps(board))
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

