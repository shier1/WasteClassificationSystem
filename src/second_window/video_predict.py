import paddle.jit
from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os
import src.modules.ui.video_mark_ui as first
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from src.modules.model_training.predict import predict_video
import cv2
import json
import threading
import glob
import time
import numpy as np

class VideoPreWin(first.Ui_MainWindow, QMainWindow):
    def __init__(self, model_dir = './model/static_model'):
        super(VideoPreWin, self).__init__()
        super().setupUi(self)#调用父类的setupUI函数
        # 播放器
        self.model_dir = model_dir
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.wgt_player)
        # 按钮
        self.btn_select.clicked.connect(self.open)      #导入
        self.star.clicked.connect(self.playPause)       #播放/暂停
        self.ensureButton.clicked.connect(self.linkdo)      #视频处理
        self.pushButton.clicked.connect(self.linkVideochange)       #播放处理的视频
        self.toolButton.clicked.connect(self.msg)
        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.outButton.clicked.connect(self.link_outfile)

    # 打开视频文件
    def open(self):
        qurl1 = QFileDialog.getOpenFileUrl()[0]
        file_url = qurl1.url()
        self.file_path = file_url.split('///')[-1]
        self.player.setMedia(QMediaContent(qurl1))
        self.player.play()

    def linkVideochange(self):
        ta = threading.Thread(target=self.Videochange)
        ta.start()

    def Videochange(self):

        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.Videoout_path)))
        self.player.play()

    # 播放视频
    def playPause(self):
        if self.player.state() == 1:
            self.player.pause()
        else:
            self.player.play()

    def linkdo(self):
        ta = threading.Thread(target=self.do)
        ta.start()

    def do(self):
        self.lineEdit_2.setText('处理中')
        self.path = os.path.join(self.lineEdit.text(), 'images')  # 图片文件路径
        self.path = self.path.replace('\\', '/')
        isExists = os.path.exists(self.path)
        if not isExists:
            os.makedirs(self.path)
        imageNum = 0
        fps = 60        #图片帧数
        self.Videoout_path = os.path.join(self.lineEdit.text(), str(int(time.time())) + ".mp4")  # 导出路径
        self.Videoout_path = self.Videoout_path.replace('\\', '/')
        capture = cv2.VideoCapture(self.file_path)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # 不同视频编码对应不同视频格式（例：'I','4','2','0' 对应avi格式）
        size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.width = size[0]
        self.height = size[-1]
        video = cv2.VideoWriter(self.Videoout_path, fourcc, fps, size, isColor=True)
        model = paddle.jit.load(self.model_dir)
        ret = True
        if not capture.isOpened():
            print("视频打开错误")
            ret = False
        print('开始处理')
        self.json_path = []
        self.fileName_list = []
        self.label_list = []
        while(ret):
            ret, frame = capture.read()
            if not ret:
                break
            res_frame, lb = predict_video(model, frame.copy())
            imageNum = imageNum + 1
            fileName = os.path.join(self.path, str(imageNum) + '.jpg')  # 存储路径
            fileName = fileName.replace('\\', '/')

            if (imageNum % 5 == 0):
                cv2.imencode('.jpg', frame)[1].tofile(fileName)
                # img = cv2.imread(fileName)  # 使用opencv读取图像，直接返回numpy.ndarray 对象，通道顺序为BGR ，注意是BGR，通道值默认范围0-255。
                json_Name = os.path.join(self.lineEdit.text(), 'json',str(imageNum) + '.json')   #json文件路径
                json_Name = json_Name.replace('\\', '/')
                self.json_path.append(json_Name)
                self.fileName_list.append(fileName)
                self.label_list.append(lb)
            video.write(res_frame)  # 把图片写进视频
        print('处理完成')
        self.lineEdit_2.setText('Finished')
        video.release()  # 释放
            # cv2.imwrite(fileName, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def msg(self,Filepath):         #储存路径
        self.m = QtWidgets.QFileDialog.getExistingDirectory(None,"选取文件夹","C:/")  # 起始路径
        self.lineEdit.setText(self.m)


    def selectionChange(self,i):

        print('current index',i,'selection changed', self.comboBox.currentText())

    def link_outfile(self):
        ta = threading.Thread(target=self.outfile)
        ta.start()

    def outfile(self):
        self.lineEdit_2.setText('导出中')
        if self.comboBox.currentText() == '.json':
            json_Name = os.path.join(self.lineEdit.text(), 'json')  # json文件路径
            json_Name = json_Name.replace('\\', '/')
            isExists = os.path.exists(json_Name)
            if not isExists:
                os.makedirs(json_Name)
            size = {'height' : self.height, 'width' :self.width}
            i = 0
            for j_path in self.json_path:
                dir = {}
                dir['name'] = self.fileName_list[i].split('/')[-1]
                dir['path'] = self.fileName_list[i]
                dir['size'] = size
                dir['tag'] = self.label_list[i]
                with open(j_path, "w", encoding='utf-8') as f:
                    json.dump(dir, f, ensure_ascii=False, indent=4)
                dir.clear()
                i+=1

        if self.comboBox.currentText() == '.txt':
            txts_Name = os.path.join(self.lineEdit.text(), 'txts')  # json文件路径
            txts_Name = txts_Name.replace('\\', '/')
            isExists = os.path.exists(txts_Name)
            if not isExists:
                os.makedirs(txts_Name)
            text1 = os.path.join(txts_Name, 'text1.txt')  # 存储路径
            text1 = text1.replace('\\', '/')
            text2 = os.path.join(txts_Name, 'text2.txt')  # 存储路径
            text2 = text2.replace('\\', '/')
            data1 = open(text1, 'w+')
            num = 0
            label_dir = {}
            judge_dir = 0
            data2 = open(text2, 'w+')
            for f_path in self.fileName_list:
                label_num = label_dir.get(self.label_list[num],'no')
                if label_num == 'no':
                    label_num = judge_dir
                    label_dir[self.label_list[num]] = label_num
                    judge_dir +=1
                    print(self.label_list[num], file=data2)
                print(f_path+'\t'+str(label_num), file=data1)
                num+=1
            data1.close()
            data2.close()
        self.lineEdit_2.setText('导出完成')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = VideoPreWin()
    ui.show()
    sys.exit(app.exec_())
