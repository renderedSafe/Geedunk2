from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAbstractButton
from PyQt5.QtCore import *


class PicButton(QAbstractButton):
    def __init__(self, pixmap, name, price, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.name = name
        self.price = price
        self.setFixedHeight(140)
        self.setFixedWidth(100)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.drawPixmap(QRect(0, 12, 100, 95), self.pixmap)
            painter.setBrush(QColor(205, 200, 200))
            top_text = QRect(0, 0, 99, 20)
            bottom_text = QRect(0, 99, 99, 20)
            painter.drawRect(top_text)
            painter.drawRect(bottom_text)
            name_font = QFont("Arial", 8, QFont.UltraCondensed)
            price_font = QFont("Times", 8, QFont.ExtraCondensed)
            painter.setFont(name_font)
            painter.drawText(top_text, Qt.AlignHCenter, self.name)
            painter.setFont(price_font)
            try:
                painter.drawText(bottom_text, Qt.AlignHCenter, ('${:.2f}'.format(float(self.price))))
            except ValueError as e:
                print(self)
                print(e)
            if self.isDown():
                painter.setBrush(QColor(0, 235, 250, 29))
                painter.drawRect(QRect(0, 0, 99, 120))
        except:
            print('painting error')

    def sizeHint(self):
        return self.pixmap.size()

    def set_name(self, name):
        self.name = name
        self.repaint()

    def set_price(self, price):
        self.price = price
        self.repaint()

    def set_icon(self, icon):
        self.pixmap = icon
        self.repaint()
