import sys

from PyQt5.QtWidgets import QApplication

from pages import central

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = central()
    widget.show()
    sys.exit(app.exec_())
