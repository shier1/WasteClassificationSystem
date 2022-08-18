import sys
from turtle import isvisible
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from src.modules.ui.Mainwindow import Ui_MainWindow, QtWidgets
from src.second_window import img_mark
from src.second_window import video_predict
from src.second_window import img_mark_folder
from src.second_window import model_train

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
        self.img_mark_folder_win = img_mark_folder.childWindow()
        self.img_mark_folder_win.show()
        self.hide()
        print(self.img_mark_folder_win.isVisible())
        
        if not self.img_mark_folder_win.isVisible():
            self.show()

    def shift_window2(self):
        self.img_mark_win = img_mark.mymainwindow()
        self.img_mark_win.show()
        self.hide()

    def shift_window3(self):
        self.video_predict_win = video_predict.myDialog()
        self.video_predict_win.show()
        self.hide()
    
    def shif_window4(self):
        self.model_train_win = model_train.TrainWin()
        self.model_train_win.show()
        self.hide()
    


if __name__=='__main__':
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec_())
