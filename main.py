import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
import qt_material

from src.modules.ui.Mainwindow import Ui_MainWindow
from src.second_window import img_mark
from src.second_window import video_predict
from src.second_window import img_mark_folder
from src.second_window import model_train
from src.second_window import video_change

class MainMenu(QMainWindow,Ui_MainWindow):
    """
    应用主菜单
    """
    def __init__(self):
        super(MainMenu,self).__init__()
        self.setupUi(self)
        self.img_mark_folder_button.clicked.connect(self.shift_window1)
        self.img_mark_button.clicked.connect(self.shift_window2)
        self.video_predict_button.clicked.connect(self.shift_window3)
        self.model_fintuning_button.clicked.connect(self.shif_window4)

    def shift_window1(self):
        self.img_mark_folder_win = img_mark_folder.ImgMarkFolderWin(self)
        self.img_mark_folder_win.show()
        self.hide()

    def shift_window2(self):
        self.img_mark_win = img_mark.ImgMaskWin(self)
        self.hide()
        self.img_mark_win.show()

    def shift_window3(self):
        # self.video_predict_win = video_predict.VideoPreWin(self)
        self.video_predict_win = video_change.VideoWin(self)
        self.hide()
        self.video_predict_win.show()
    
    def shif_window4(self):
        self.model_train_win = model_train.TrainWin(self)
        self.hide()
        self.model_train_win.show()


if __name__=='__main__':
    app = QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme='dark_teal.xml')
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec_())