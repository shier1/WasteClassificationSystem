from PyQt5.QtWidgets import  QWidget, QMessageBox
from PyQt5.QtGui import QCloseEvent

from src.modules.ui.train_ui import Ui_Form

class TrainWin(Ui_Form, QWidget):
    def __init__(self, main_menu_win):
        super(TrainWin, self).__init__()
        self.main_menu_win = main_menu_win
        self.setupUi(self)

    def closeEvent(self, a0: QCloseEvent) -> None:
        reply = QMessageBox.question(self,
                                     "本程序",
                                     "是否回到主窗口",
                                     QMessageBox.Yes|QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.main_menu_win.show()
            return super().closeEvent(a0)
        else:
            return super().closeEvent(a0)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     train_win = TrainWin()
#     train_win.show()
#     sys.exit(app.exec_())