from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class LogThread(QtCore.QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, gui):
        super(LogThread, self).__init__()
        self.gui = gui

    def run(self) -> None:
        while True:
            if not self.gui.Q.empty():
                pieceLog = self.gui.Q.get_nowait()
                self.sinOut.emit(str(pieceLog))
            # self.msleep(10)
