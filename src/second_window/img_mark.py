import os
import cv2
import json
import numpy as np
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QCloseEvent, QPixmap

from src.modules.ui.img_mark_ui import Ui_Form
from src.modules.model_training.predict import predict_one_image


class ImgMaskWin(QWidget,Ui_Form):
    def __init__(self, main_menu_win, model_path = 'src/modules/model_training/model/static_model'):
        super().__init__()
        self.setupUi(self,)
        self.pushButton.clicked.connect(self.openimage)  #绑定按键1，打开文件图片
        self.pushButton_2.clicked.connect(self.saveJsonFile) #绑定按键2，保存json文件
        self.pushButton_3.clicked.connect(self.clearimage)  #绑定按键3，清空图片重新开始
        self.pushButton_4.clicked.connect(self.startidentify) #绑定按键4，识别图片
        self.pushButton_5.clicked.connect(self.saveFile) #绑定按键5，选择保存文件夹
        self.model_path = model_path
        self.main_menu_win = main_menu_win


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

    def saveFile(self):
        self.path = QFileDialog.getExistingDirectory(self,'选择保存文件夹','')
        self.path = self.path
        self.lineEdit_2.setText(self.path)
        os.makedirs(os.path.join(self.path, 'images').replace('\\', '/'), exist_ok=True)    #创建存放原图的文件夹，用makedirs函数
        os.makedirs(os.path.join(self.path, 'labels').replace('\\', '/'), exist_ok=True)   #创建存放json文件的文件夹

    def openimage(self):    #读取文件图片
        self.imgName, self.imgType = QFileDialog.getOpenFileName(self, "导入照片", "", "*.jpg;;*.png;;*jpeg;;*JPEG;;All Files(*)") #导入图片路径
        jpg = QPixmap(self.imgName).scaled(self.label_2.width(), self.label_2.height())  #将图片设置成适合label的尺寸
        self.label_2.setPixmap(jpg)  #在label框显示出图片
        self.lineEdit.setText('')  # 重置用户提示框

    def clearimage(self):  #清空已经打开的图片
        self.label_2.setPixmap(QPixmap("")) #重置label中的图片
        self.lineEdit.setText('') #重置识别框


    def startidentify(self):   #识别图片信息，标签
        image = cv2.imdecode(np.fromfile(self.imgName, dtype=np.uint8), cv2.IMREAD_COLOR)  #读取中文路径的图片
        val = predict_one_image(self.model_path, image)
        self.lineEdit.setText(val)

    def saveJsonFile(self):   #保存图片信息的json文件
        image = cv2.imdecode(np.fromfile(self.imgName, dtype=np.uint8), cv2.IMREAD_COLOR)  #读取中文路径的图片
        imgheight = image.shape[0]
        imgwidth = image.shape[1]
        '''打印出长宽'''
        size = {
            'height':imgheight,
            'width':imgwidth
               }
        tag = self.lineEdit.text()    #tag获取lineedit里面的值
        image_relative_path = os.path.split(self.imgName)[1]       #os.path.split(绝对路径)分开为目录和文件名
        cv2.imencode('.jpg', image)[1].tofile(os.path.join(self.path, 'image', image_relative_path).replace('\\', '/'))
        imagemeeage = {'name':image_relative_path,
                       'path':os.path.join(self.path, 'image', image_relative_path).replace('\\', '/'),
                       'size':size,
                       'tag':tag
                       }
        imagename = image_relative_path.split('.')[0]
        imagemeeage_json = json.dumps(imagemeeage, ensure_ascii=False, indent=2)
        #拼接路径，用函数拼接更加灵活
        with open(os.path.join(self.path,'label', imagename+'.json').replace('\\', '/'), 'w') as f:
            f.write(imagemeeage_json)
        QMessageBox.information(self,'提式','导出图片及标签成功')

# if __name__=='__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     window = ImgMaskWin()
#     window.show()
#     sys.exit(app.exec_())