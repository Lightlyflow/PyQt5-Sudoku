from PyQt5.QtCore import QTimer, QTime, QObject, pyqtSignal, Q_ENUMS, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class State:
    # https://stackoverflow.com/questions/53405789/make-a-simple-stopwatch-stoppable
    STOPPED = 0
    PAUSE = 1
    RUNNING = 2


class StopwatchObject(QObject, State):
    State = State
    Q_ENUMS(State)

    secondChanged = pyqtSignal(int)
    minuteChanged = pyqtSignal(int)
    hourChanged = pyqtSignal(int)
    stateChanged = pyqtSignal(State)

    def __init__(self, parent=None):
        super(StopwatchObject, self).__init__(parent)
        self._current_state = State.STOPPED
        self._time = QTime()
        self._timer = QTimer(self, interval=100, timeout=self.on_timeout)
        self._delta = 0
        self.seconds = 0
        self.minutes = 0
        self.hours = 0

    def setCurrentState(self, state):
        self._current_state = state
        self.stateChanged.emit(state)

    def setTime(self, h: int, m: int, s: int):
        self.hours = h
        self.minutes = m
        self.seconds = s
        self.start()

    @pyqtSlot()
    def start(self):
        self._delta = 0
        self._timer.start()
        self._time.start()
        self.setCurrentState(State.RUNNING)

    @pyqtSlot()
    def stop(self):
        if self._current_state != State.STOPPED:
            self._timer.stop()
            self.setCurrentState(State.STOPPED)

    @pyqtSlot()
    def pause(self):
        if self._current_state == State.RUNNING:
            self._timer.stop()
            self.setCurrentState(State.PAUSE)
            self._delta += self._time.elapsed()

    @pyqtSlot()
    def resume(self):
        if self._current_state == State.PAUSE:
            self._timer.start()
            self._time = QTime()
            self._time.start()
            self.setCurrentState(State.RUNNING)

    @pyqtSlot()
    def on_timeout(self):
        t = QTime.fromMSecsSinceStartOfDay(self._delta + self._time.elapsed())
        s, m, h = t.second(), t.minute(), t.hour()
        if self.seconds != s:
            self.seconds = s
            self.secondChanged.emit(s)

        if self.minutes != m:
            self.minutes = m
            self.minuteChanged.emit(m)

        if self.hours != h:
            self.hours = h
            self.hourChanged.emit(h)


class StopwatchWidget(QWidget):
    def __init__(self, parent=None):
        super(StopwatchWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.stopwatch_object = StopwatchObject(self)
        self.label = QLabel("0:00")
        self.label.setObjectName("stopwatch")
        self.stopwatch_object.secondChanged.connect(self.updateText)
        self.stopwatch_object.minuteChanged.connect(self.updateText)
        self.stopwatch_object.hourChanged.connect(self.updateText)
        self.layout().setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.label)

    def start(self):
        self.stopwatch_object.start()

    def stop(self):
        self.stopwatch_object.stop()

    def pause(self):
        self.stopwatch_object.pause()

    def resume(self):
        self.stopwatch_object.resume()

    def reset(self):
        self.stopwatch_object.setTime(0, 0, 0)

    def setTime(self, h: int, m: int, s: int):
        self.stopwatch_object.setTime(h, m, s)

    def getTime(self) -> str:
        return f"{self.stopwatch_object.hours}:{self.stopwatch_object.minutes}:{self.stopwatch_object.seconds}"

    @pyqtSlot()
    def updateText(self):
        text = "{:d}:{:d}:{:02d}".format(self.stopwatch_object.hours, self.stopwatch_object.minutes, self.stopwatch_object.seconds)
        self.label.setText(text)
