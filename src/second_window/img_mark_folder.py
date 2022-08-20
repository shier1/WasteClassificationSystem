import os
import cv2
import json
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QApplication
from PyQt5.QtGui import QImage,QPixmap, QCloseEvent

from src.modules.ui.img_mark_folder_ui import Ui_Form


class ImgMarkFolderWin(Ui_Form,QWidget):
    def __init__(self,main_menu_win):
        super(ImgMarkFolderWin, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("图像标注")   # 设置窗口名
        self.main_menu_win = main_menu_win
        self.pushButton_4.clicked.connect(self.ChoicefileImage)#打开图片
        self.comboBox.setEditable(True)
        self.comboBox.lineEdit().setPlaceholderText("新建标签")
        self.pushButton_3.clicked.connect(self.putimage)
        self.pushButton_2.clicked.connect(self.next)
        self.pushButton_6.clicked.connect(self.open2)
        self.pushButton_5.clicked.connect(self.quding)
        self.pushButton.clicked.connect(self.previous)
        self.listWidget.itemClicked.connect(self.Image)
        self.listWidget.verticalScrollBar().valueChanged.connect(lambda: ...)
        self.path_1 = None

    def closeEvent(self, a0: QCloseEvent) -> None:
        reply = QMessageBox.question(self,
                                     "本程序",
                                     "是否返回主菜单？",
                                     QMessageBox.Yes|QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.main_menu_win.show()
            return super().closeEvent(a0)
        else:
            return super().closeEvent(a0) 

    def open2(self):
        self.path_1=QFileDialog.getExistingDirectory(self, "选择保存路径","/")
        self.lineEdit_3.setText(self.path_1)
	# #当窗口非继承QtWidgets.QDialog时，self需替换成 None

    def quding(self):
        curent_row = self.listWidget.currentRow()
        label = self.comboBox.currentText()
        if label:
            self.dict_[self.image_path_list[curent_row]] = label
            self.show_label()
        else:
            QMessageBox.information(self,'提示','标签不能为空')

    def show_label(self):
        curent_row = self.listWidget.currentRow()
        lable = self.dict_[self.image_path_list[curent_row]]
        self.lineEdit.setText(lable)

    def open_root(self):
        self.file_path= QFileDialog.getExistingDirectory(self, '选择文文件夹', '/')#打开文件夹

    def Image(self):                            #打开listwidget和主label
        self.item=self.listWidget.selectedItems()[0]
        for i in range(self.photo_num):
            if str(i)+" "+self.image_path_list[i]==self.item.text():
                path = os.path.join(self.file_path, self.image_path_list[i]).replace('\\', '/')
                self.imageshow(path)
                self.show_label()


    def imageshow(self,file_path):
        pixmap = QPixmap(file_path).scaled(self.label.width(), self.label.height())
        self.label.setPixmap(pixmap)
        self.lineEdit_2.setText(file_path)
        #self.comboBox.currentText()




    def check_image(self, path:str):
        path = path.lower()
        if path.endswith('jpg') or path.endswith('png') or path.endswith('jpeg'):
            return True
        else:
            return False


    def ChoicefileImage(self):
        self.open_root()
        if self.file_path:
            self.path_list = os.listdir(self.file_path)
            self.image_path_list = [path for path in self.path_list if self.check_image(path)]
            self.photo_num = len(self.image_path_list)
            self.dict_={}
            if self.photo_num != 0:
                for i in range(self.photo_num):
                    path = self.image_path_list[i]
                    self.listWidget.addItem(str(i)+" "+path)
                    self.dict_[path] = ""
                    QApplication.processEvents()  ##实时加载，可能图片加载数量比较多
                # 将第一个item设置为已选择的item，并显示图片
                self.item = self.listWidget.item(0)
                self.listWidget.setCurrentItem(self.item)
                path = os.path.join(self.file_path, self.image_path_list[0]).replace('\\', '/')
                self.imageshow(path)
                self.show_label()
            else:
                QMessageBox.information(self, '提示', '该文件夹图片为空')
        else:
            QMessageBox.information(self, '提示', '请先选择根文件夹')

    def putimage(self):
        if self.path_1 :
            image_dir = os.path.join(self.path_1,"images").replace('\\', '/')
            os.makedirs(image_dir, exist_ok=True)
            if self.comboBox_2.currentText()==".json":
                dir_path1 = os.path.join(self.path_1,'label_json').replace('\\', '/')
                os.makedirs(dir_path1, exist_ok=True)
                for i in range(self.photo_num):
                    if self.dict_[self.image_path_list[i]]!="":
                        img =  cv2.imdecode(np.fromfile(os.path.join(self.file_path,self.image_path_list[i]).replace("\\","/"), dtype=np.uint8),-1)
                        cv2.imencode('.jpg', img)[1].tofile(os.path.join(image_dir,self.image_path_list[i]).replace("\\","/"))
                        label = {
                            "name": self.image_path_list[i],
                            "path": self.file_path,
                            "size":
                                {
                                    "height": img.shape[0],
                                    "width": img.shape[1]
                                },
                            "tag": self.dict_[self.image_path_list[i]]
                        }
                        label_json = json.dumps(label, ensure_ascii=False, indent=2)
                        image_path = os.path.join(dir_path1, self.image_path_list[i].split('.')[0]+'.json').replace('\\', '/')
                        with open(image_path,"w") as f:
                            f.write(label_json)
                QMessageBox.information(self,"提示","成功导入json文件")
            else:
                dir_path2 = os.path.join(self.path_1, 'label_txt').replace('\\', '/')
                os.makedirs(dir_path2, exist_ok=True)
                j=0
                dict_1={}
                for i in range(self.photo_num):
                    if self.dict_[self.image_path_list[i]] != "":
                        img = cv2.imdecode(np.fromfile(os.path.join(self.file_path, self.image_path_list[i]).replace("\\", "/"),dtype=np.uint8), -1)
                        cv2.imencode('.jpg', img)[1].tofile(os.path.join(image_dir, self.image_path_list[i]).replace("\\", "/"))
                        image_path2 = os.path.join(dir_path2,"1.txt")

                        #print(self.dict_[self.image_path_list[i]])
                        if self.dict_[self.image_path_list[i]] not in dict_1.keys():
                            dict_1[self.dict_[self.image_path_list[i]]]=str(j)
                            j=j+1

                print(dict_1)
                print(self.dict_)
                image_path2 = os.path.join(dir_path2, "1.txt").replace('\\','/')
                image_path3 = os.path.join(dir_path2, "2.txt").replace('\\','/')
                print(image_path3)
                with open(image_path2, "w",encoding='utf-8') as f:
                    for i in range(self.photo_num):
                        print(123)
                        if self.dict_[self.image_path_list[i]] != "":
                         xieru = os.path.join(image_dir,self.image_path_list[i]).replace('\\','/')
                         xieru2 = xieru + '\t' +dict_1[self.dict_[self.image_path_list[i]]]+'\n'
                         f.write(xieru2)
                with open(image_path3,"w",encoding='utf-8') as f1:
                    for t in dict_1.keys():
                        f1.write(t+"\n")
                QMessageBox.information(self, "提示", "成功导入txt文件")
        else:
            QMessageBox.information(self, "提示", "请选择导出路径")

    def next(self):
        self.item = self.listWidget.currentItem()
        if self.item == self.listWidget.item(self.listWidget.count()-1):
            QMessageBox.information(self,'提式','已经到达最后一张')
        else:
            current_row = self.listWidget.currentRow()
            current_row += 1
            self.listWidget.setCurrentItem(self.listWidget.item(current_row))
            path = os.path.join(self.file_path, self.image_path_list[current_row]).replace('\\', '/')
            self.imageshow(path)
            self.show_label()


    def previous(self):
        self.item = self.listWidget.currentItem()
        if self.item == self.listWidget.item(0):
            QMessageBox.information(self,'提式','已经到达第一张')
        else:
            curent_row = self.listWidget.currentRow()
            curent_row -= 1
            self.listWidget.setCurrentItem(self.listWidget.item(curent_row))
            path = os.path.join(self.file_path, self.image_path_list[curent_row]).replace('\\', '/')
            self.imageshow(path)
            self.show_label()


# if __name__=='__main__':
#     app = QApplication(sys.argv)
#     window = ImgMarkFolderWin()
#     window.show()
#     sys.exit(app.exec_())