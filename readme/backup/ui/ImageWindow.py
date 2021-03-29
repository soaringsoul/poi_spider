from PyQt5.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout

from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5 import QtCore, QtGui, QtWidgets


class ImageWindow(QMainWindow):
    def __init__(self, resources, title):
        super(ImageWindow, self).__init__()
        self.setWindowTitle(title)



        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        # layout=QGridLayout(self.central_widget)

        pixmap = QPixmap(resources)
        image_label = QLabel(self)
        image_label.setPixmap(pixmap)

        image_label.resize(pixmap.width(), pixmap.height())
        self.setFixedSize(pixmap.width(), pixmap.height())
        image_label.setScaledContents(True)
        layout.addWidget(image_label)
