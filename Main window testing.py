from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore, uic
from PicButton import PicButton


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(50, 50, 1000, 980)
        self.central_widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()

        picButton = PicButton(QPixmap('egg6.png'), 'Hot Pocket', .5)
        layout.addWidget(picButton)
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()