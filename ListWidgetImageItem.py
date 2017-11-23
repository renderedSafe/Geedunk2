from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon


class ListWidgetImageItem(QListWidgetItem):
    def __init__(self, icon, value, parent=None):
        super(ListWidgetImageItem, self).__init__(parent)
        self.setIcon(QIcon(icon))
        self.value = value
