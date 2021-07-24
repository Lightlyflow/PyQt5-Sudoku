import sys

from PyQt5.QtWidgets import QApplication

from pages import Game, SudokuApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = SudokuApp()
    widget.show()
    sys.exit(app.exec_())
