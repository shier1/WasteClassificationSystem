import cv2
import json
import threading
import time
import os
import paddle.jit
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage,QPixmap, QCloseEvent

from src.modules.ui import video_change_ui
from src.modules.model_training.predict import predict_video


class VideoWin(video_change_ui.Ui_MainWindow, QMainWindow):
    def __init__(self, main_menu_win, model_dir = 'src/modules/model_training/model/static_model'):
        super(VideoWin, self).__init__()
        super().setupUi(self,)#调用父类的setupUI函数
        self.label_3.setStyleSheet("QLabel{background:black;}"
                                 "QLabel{color:rgb(100,100,100);font-size:15px;font-weight:bold;font-family:宋体;}"
                                 )
        self.btn_select.clicked.connect(self.open)      #导入
        self.star.clicked.connect(self.playPause)       #播放/暂停
        self.ensureButton.clicked.connect(self.linkdo)      #视频处理
        self.pushButton.clicked.connect(self.linkVideochange)       #播放处理的视频
        self.toolButton.clicked.connect(self.msg)
        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.outButton.clicked.connect(self.link_outfile)
        # 播放器
        self.model_dir = model_dir
        self.main_menu_win = main_menu_win
        self.frame = []  # 存图片
        self.cap = []
        self.x = 0
        self.flag1 = False  # 是否进行模型处理
        self.flag2 = False  # 是否保存抽帧图片
        self.flag3 = False  # 是否显示图片合成的视频
        self.flag4 = False  # 对视频播放和暂停的按钮
        self.timer_camera = QTimer()  # 定义定时器

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
    # 打开视频文件
    def open(self):
        self.videoName, _ = QFileDialog.getOpenFileName(self, "Open", "", "*.mp4;;*.avi;;All Files(*)")
        if self.videoName != "":  # “”为用户取消
            self.cap = cv2.VideoCapture(self.videoName)
            self.timer_camera.start(30)
            self.timer_camera.timeout.connect(self.openFrame)

    def openFrame(self):
        if (self.cap.isOpened()):
            ret, self.frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                q_image = QImage(frame.data, width, height, bytesPerLine,
                                 QImage.Format_RGB888)
                self.label_3.setPixmap(QPixmap.fromImage(q_image.scaled(self.label_3.width(), self.label_3.height())))
            else:
                self.cap.release()
                self.timer_camera.stop()  # 停止计时器
    def linkVideochange(self):
        self.cap = cv2.VideoCapture(self.Videoout_path)
        self.timer_camera.start(30)
        self.timer_camera.timeout.connect(self.openFrame)

    def Videochange(self):
        pass
    # 播放视频
    def playPause(self):
        if self.flag4 == True:
            self.timer_camera.start(30)
            self.flag4 = False
        else:
            self.timer_camera.stop()
            self.flag4 = True

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
        capture = cv2.VideoCapture(self.videoName)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # 不同视频编码对应不同视频格式（例：'I','4','2','0' 对应avi格式）
        size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.width = size[0]
        self.height = size[-1]
        video = cv2.VideoWriter(self.Videoout_path, fourcc, fps, size, isColor=True)
        model = paddle.jit.load(self.model_dir)
        ret = True
        if not capture.isOpened():
            QMessageBox.information(self, "错误", "视频打开失败")
            ret = False
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
        print()
        self.lineEdit_2.setText('Finished')
        video.release()  # 释放
            # cv2.imwrite(fileName, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])






    def msg(self,Filepath):         #储存路径
        self.m = QtWidgets.QFileDialog.getExistingDirectory(None,"选取文件夹","C:/")  # 起始路径
        self.lineEdit.setText(self.m)


    def selectionChange(self,i):
        QMessageBox.information(self, "提示", f'current index {i} selection changed {self.comboBox.currentText()}')

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
            text1 = os.path.join(txts_Name, 'train.txt')  # 存储路径
            text1 = text1.replace('\\', '/')
            text2 = os.path.join(txts_Name, 'labellist.txt')  # 存储路径
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


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     ui = VideoWin()
#     ui.show()
#     sys.exit(app.exec_())