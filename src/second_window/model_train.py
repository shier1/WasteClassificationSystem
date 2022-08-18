import sys
import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget

from src.modules.ui.train_ui import Ui_Form

class TrainWin(Ui_Form, QWidget):
    def __init__(self, ):
        super(TrainWin, self).__init__()
        self.setupUi(self)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    train_win = TrainWin()
    train_win.show()
    sys.exit(app.exec_())