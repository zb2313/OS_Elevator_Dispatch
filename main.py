import sys, threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QPainter

from ElevatorUI import *
from scheduling import *

class elevatorPage(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(elevatorPage, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Elevator-dispatch')
        self.setWindowIcon(QIcon('D:/Resources/Icon.png'))

    def paintEvent(self, event):
        painter = QPainter(self)
        # todo 1 设置背景颜色
        painter.setBrush(Qt.white)
        painter.drawRect(self.rect())

        # #todo 2 设置背景图片，平铺到整个窗口，随着窗口改变而改变
        # pixmap = QPixmap("./images/screen1.jpg")
        # painter.drawPixmap(self.rect(), pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    page = elevatorPage()
    page.resize(1250, 860)
    page.show()

    sys.exit(app.exec())