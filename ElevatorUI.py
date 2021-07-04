from PyQt5 import QtCore, QtGui, QtWidgets
from scheduling import MyScheduling
from PyQt5.QtCore import *

STANDSTILL = 0  # 静止状态
RUNNING_UP = 1  # 上行状态
RUNNING_DOWN = 2  # 下行状态

NOPE = 0  # 空动画
READYSTART = 1  # 准备运动
READYSTOP = 2  # 即将停止

GOUP = 1  # 上行
GODOWN = 2  # 下行

OPEN = 0  # 开门状态
CLOSED = 1  # 关门状态

class Ui_MainWindow(object):
    def __init__(self):


        self.schedule = MyScheduling(self)  # 与调度文件连接

    def setupUi(self, MainWindow):
        self.upbtn_style = "QPushButton{border-image: url(Resources/up_hover.png)}" \
                           "QPushButton:hover{border-image: url(Resources/up.png)}" \
                           "QPushButton:pressed{border-image: url(Resources/up_pressed.png)}"
        self.downbtn_style = "QPushButton{border-image: url(Resources/down_hover.png)}" \
                             "QPushButton:hover{border-image: url(Resources/down.png)}" \
                             "QPushButton:pressed{border-image: url(Resources/down_pressed.png)}"
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 700)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.elevEnabled = [True] * 5  # 电梯状态(可使用/禁用)标志位
        self.doorState = [CLOSED] * 5  # 电梯门状态(开门/关门)标志位
        self.elevState = [STANDSTILL] * 5  # 电梯状态(运行向上/运行向下/静止)标志位
        self.animState = [NOPE] * 5  # 动画播放状态(空/即将运动/即将停止)标志位
        self.elevNow = [1] * 5  # 电梯楼层

        # region 边界
        boundPos = [10, 180, 360, 540, 720, 890]
        self.bounder = []  # 电梯边界
        self.level = []  # 电梯层界
        for i in range(0, len(boundPos)):
            self.bounder.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.bounder[i].setGeometry(QtCore.QRect(boundPos[i], 120, 1, 700))
            self.bounder[i].setAutoFillBackground(False)
            self.bounder[i].setStyleSheet("background-color: rgb(0, 0, 0);")
            self.bounder[i].setObjectName("wall" + str(i))
        # endregion

        # region 电梯
        self.elevator_back = []  # 电梯背景
        self.elevator_front = [] #电梯门
        self.elevator_Anim = [] #电梯动画
        elevator_pos = [30, 200, 380, 560, 740]

        for i in range(0, len(elevator_pos)):
            # 电梯背景
            self.elevator_back.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.elevator_back[i].setGeometry(QtCore.QRect(elevator_pos[i], 610, 131, 161))
            self.elevator_back[i].setStyleSheet("background-color: rgb(87, 87, 87);")
            self.elevator_back[i].setObjectName("elevator_back" + str(i))

            # 两扇电梯门
            self.elevator_front.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.elevator_front[2 * i].setGeometry(QtCore.QRect(elevator_pos[i], 610, 64, 161))
            self.elevator_front[2 * i].setStyleSheet("background-color: rgb(160, 160, 160);")
            self.elevator_front[2 * i].setObjectName("elevator_front" + str(2 * i))
            self.elevator_Anim.append(QPropertyAnimation(self.elevator_front[2 * i], b"geometry"))
            self.elevator_Anim[2 * i].setDuration(1000)  # 设定动画时间
            self.elevator_Anim[2 * i].setStartValue(QtCore.QRect(elevator_pos[i], 610, 64, 161))  # 设置起始大小
            self.elevator_Anim[2 * i].setEndValue(QtCore.QRect(elevator_pos[i], 610, 8, 161))  # 设置终止大小

            self.elevator_front.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.elevator_front[2 * i + 1].setGeometry(QtCore.QRect(elevator_pos[i] + 67, 610, 64, 161))
            self.elevator_front[2 * i + 1].setStyleSheet("background-color: rgb(160, 160, 160);")
            self.elevator_front[2 * i + 1].setObjectName("elevator_front" + str(2 * i + 1))
            self.elevator_Anim.append(QPropertyAnimation(self.elevator_front[2 * i + 1], b"geometry"))
            self.elevator_Anim[2 * i + 1].setDuration(1000)
            self.elevator_Anim[2 * i + 1].setStartValue(QtCore.QRect(elevator_pos[i] + 67, 610, 64, 161))
            self.elevator_Anim[2 * i + 1].setEndValue(QtCore.QRect(elevator_pos[i] + 123, 610, 8, 161))
        # endregion

        # region 电梯号码
        font = QtGui.QFont()
        font.setFamily("AcadEref")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)

        self.label = []
        label_pos = [70, 240, 420, 600, 780]
        for i in range(0, len(label_pos)):
            self.label.append(QtWidgets.QLabel(self.centralwidget))
            self.label[i].setGeometry(QtCore.QRect(label_pos[i], 800, 51, 21))
            self.label[i].setFont(font)
            self.label[i].setStyleSheet("font: 10pt \"AcadEref\";\n"
                                        "background-color: rgb(160, 160, 160);")
            self.label[i].setObjectName("label" + str(i))

        self.label2 = []
        label_pos2 = [170+i*40 for i in range(0,5)]
        for i in range(0, len(label_pos2)):
            self.label2.append(QtWidgets.QLabel(self.centralwidget))
            self.label2[i].setGeometry(QtCore.QRect(label_pos2[i]+765, 810, 21, 21))
            self.label2[i].setFont(font)
            self.label2[i].setStyleSheet("font: 10pt \"AcadEref\";\n"
                                        "background-color: rgb(160, 160, 160);")
            self.label2[i].setObjectName("label2" + str(i))

        # endregion

        # region 电梯楼层显示
        self.lcdNumber = []  # 数码管
        lcdNumber_pos = [50, 220, 400, 580, 760]
        for i in range(0, len(lcdNumber_pos)):
            self.lcdNumber.append(QtWidgets.QLCDNumber(self.centralwidget))
            self.lcdNumber[i].setGeometry(QtCore.QRect(lcdNumber_pos[i]-10, 110, 51, 41))
            self.lcdNumber[i].setDigitCount(2)
            self.lcdNumber[i].setProperty("value", 1.0)  # 设置初始楼层为1层
            self.lcdNumber[i].setObjectName("lcdNumber" + str(i))
        # endregion

        # region 电梯上下行标志
        self.stateshow = []  # 上下行标志
        stateshow_pos = [95, 265, 445, 625, 805]
        for i in range(0, len(stateshow_pos)):
            self.stateshow.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.stateshow[i].setGeometry(QtCore.QRect(stateshow_pos[i], 100, 71, 61))
            self.stateshow[i].setStyleSheet("QGraphicsView{border-image: url(Resources/state.png)}")
            self.stateshow[i].setObjectName("stateshow" + str(i))
        # endregion

        # region 电梯停用
        self.warnbtn = []  # 报警器
        warnbtn_pos = [90, 260, 440, 620, 800]
        for i in range(0, len(warnbtn_pos)):
            self.warnbtn.append(QtWidgets.QPushButton(self.centralwidget))
            self.warnbtn[i].setGeometry(QtCore.QRect(warnbtn_pos[i] + 10, 60, 56, 31))
            self.warnbtn[i].setStyleSheet("background-color: rgb(180, 0, 0);")
            self.warnbtn[i].setObjectName("warnbtn" + str(i))

        # 连接监听器
        for i in range(0, len(self.warnbtn)):
            self.warnbtn[i].clicked.connect(MainWindow.connectStopListener)

        # endregion

        # region 数字按键
        self.gridLayoutWidget = []
        self.gridLayout = []
        gridLayoutWidget_pos = [30, 200, 380, 560, 740]

        for i in range(0, len(gridLayoutWidget_pos)):
            self.gridLayoutWidget.append(QtWidgets.QWidget(self.centralwidget))
            self.gridLayoutWidget[i].setGeometry(QtCore.QRect(gridLayoutWidget_pos[i] + 10, 120, 120, 451))
            self.gridLayoutWidget[i].setObjectName("gridLayoutWidget" + str(i))
            self.gridLayout.append(QtWidgets.QGridLayout(self.gridLayoutWidget[i]))
            self.gridLayout[i].setContentsMargins(0, 0, 0, 0)
            self.gridLayout[i].setObjectName("gridLayout" + str(i))

        num = ['17', '18', '19', '20', '13', '14', '15', '16', '9', '10', '11', '12', '5', '6', '7', '8', '1', '2',
                 '3', '4']
        positions = [(i, j) for i in range(5) for j in range(4)]
        for i in range(0, len(gridLayoutWidget_pos)):
            for position, name in zip(positions, num):
                button = QtWidgets.QPushButton(name)
                button.setObjectName("button " + str(i) + ' ' + name)
                button.setStyleSheet("")
                button.clicked.connect(MainWindow.connectNumListener)
                self.gridLayout[i].addWidget(button, *position)
        # endregion

        # region 电梯内部开关门按钮
        self.openbtn = []
        self.closebtn = []
        openbtn_pos = [60, 230, 410, 590, 770]
        closebtn_pos = [110, 280, 460, 640, 820]

        for i in range(0, len(openbtn_pos)):
            self.openbtn.append(QtWidgets.QPushButton(self.centralwidget))
            self.openbtn[i].setGeometry(QtCore.QRect(openbtn_pos[i]-15, 560, 31, 31))
            self.openbtn[i].setStyleSheet("QPushButton{border-image: url(Resources/open.png)}"
                                              "QPushButton:hover{border-image: url(Resources/open_hover.png)}"
                                              "QPushButton:pressed{border-image: url(Resources/open_pressed.png)}")
            self.openbtn[i].setObjectName("openbtn" + str(i))

            self.closebtn.append(QtWidgets.QPushButton(self.centralwidget))
            self.closebtn[i].setGeometry(QtCore.QRect(closebtn_pos[i] +10, 560, 31, 31))
            self.closebtn[i].setStyleSheet("QPushButton{border-image: url(Resources/close.png)}"
                                          "QPushButton:hover{border-image: url(Resources/close_hover.png)}"
                                          "QPushButton:pressed{border-image: url(Resources/close_pressed.png)}")
            self.closebtn[i].setObjectName("closebtn" + str(i))

            self.openbtn[i].clicked.connect(MainWindow.connectDoorListener)  # 绑定门开关键槽函数
            self.closebtn[i].clicked.connect(MainWindow.connectDoorListener)
        # endregion

        # region 小人模型
        self.figure = []  # 小人
        self.figure_Anim = []
        figure_pos = [10, 180, 360, 540, 720]
        for i in range(0, len(figure_pos)):
            self.figure.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.figure[i].setGeometry(QtCore.QRect(figure_pos[i] , 690, 71, 71))
            self.figure[i].setStyleSheet("QGraphicsView{border-image: url(Resources/people.png)}")
            self.figure[i].setVisible(False)
            self.figure[i].setObjectName("figure" + str(i))
            self.figure_Anim.append(QPropertyAnimation(self.figure[i], b"geometry"))
            self.figure_Anim[i].setDuration(1500)
            self.figure_Anim[i].setStartValue(QtCore.QRect(figure_pos[i] - 20, 690, 71, 71))
            self.figure_Anim[i].setEndValue(QtCore.QRect(figure_pos[i] + 10, 610, 111, 121))
        # endregion

        # region 电梯每一层数字

        self.number_btn = [[] for i in range(1)]  # 为使索引序号与电梯序号对应起来，创建六个子数组，第0个不加操作
        self.number_btn[0].append(0)  # 为使索引序号与电梯楼层对应起来，在第0个位置添加空项，用0替代
        for j in range(1, 21):
            self.number_btn[0].append(QtWidgets.QGraphicsView(MainWindow))  # 创建一个按钮，并将按钮加入到窗口MainWindow中
            self.number_btn[0][j].setGeometry(QtCore.QRect(900, 810.5 - j * 40, 35, 35))
            self.number_btn[0][j].setStyleSheet("QGraphicsView{border-image: url(Resources/number/" + str(j) + "_hover.png)}")
        # endregion

        #region 每层楼的上下行按键
        self.up_btn = {}
        for i in range(1, 20):
            self.up_btn[i] = QtWidgets.QPushButton(MainWindow)
            self.up_btn[i].setGeometry(QtCore.QRect(1120, 810 - i * 40, 35, 35))
            self.up_btn[i].setStyleSheet(self.upbtn_style)
            self.up_btn[i].setObjectName("upbtn"+str(i))
            self.up_btn[i].clicked.connect(MainWindow.connectDirListener)
        self.down_btn = {}
        for i in range(2, 21):
            self.down_btn[i] = QtWidgets.QPushButton(MainWindow)
            self.down_btn[i].setGeometry(QtCore.QRect(1170, 810 - i * 40, 35, 35))
            self.down_btn[i].setStyleSheet(self.downbtn_style)
            self.down_btn[i].setObjectName("downbtn" + str(i))
            self.down_btn[i].clicked.connect(MainWindow.connectDirListener)
        #endregion

        #region 小电梯png
        self.elevator_label = {}
        for i in range(0, 5):
            self.elevator_label[i] = QtWidgets.QLabel(MainWindow)
            self.elevator_label[i].setPixmap(QtGui.QPixmap("Resources/elevator.png"))
            self.elevator_label[i].setGeometry(QtCore.QRect((i+1)* 40 +900, 770, 10, 35))
            self.elevator_label[i].setScaledContents(True)
        #endregion
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        for i in range(0, len(self.label)):
            self.label[i].setText(_translate("MainWindow", "ele" + str(i)))
            self.label2[i].setText(_translate("MainWindow", str(i)))
            self.warnbtn[i].setText(_translate("MainWindow", "alarm"))


    def connectStopListener(self):
        which_warnbtn = int(self.sender().objectName()[-1])
        print("点击了{0}号报警器".format(which_warnbtn))
        self.warnbtn[which_warnbtn].setStyleSheet("background-color: rgb(255, 255, 255);")
        self.MessBox = QtWidgets.QMessageBox.information(self.warnbtn[int(which_warnbtn)], "warning",  # 弹出警告框
                                                         "第" + str(which_warnbtn) + "号电梯停止使用")
        self.warnbtn[which_warnbtn].setStyleSheet("background-color: rgb(180, 0, 0);")

        self.schedule.stopUsingListen(which_warnbtn)  # 调用控制器进行warnCtrl处理


    def connectDoorListener(self):
        objectName = self.sender().objectName()
        whichelev = int(objectName[-1])
        whichcommand = 0 if objectName[0] == 'o' else 1  # 0 => 开门    1 => 关门
        print("{0}号电梯, 命令是{1}".format(whichelev, whichcommand))

        self.schedule.doorListen(whichelev, whichcommand)  # 调用控制器进行doorCtrl处理


    def connectNumListener(self):
        whichbtn = self.sender()

        btn_name = whichbtn.objectName()
        buf = [int(s) for s in btn_name.split() if s.isdigit()]  # 提取字符串中的数字
        whichelev = buf[0]
        whichfloor = buf[1]
        print("{0}号电梯, {1}按键被按".format(whichelev, whichfloor))

        whichbtn.setStyleSheet("background-color: rgb(255, 150, 3);")  # 改变按钮背景颜色(模拟点击状态)
        whichbtn.setEnabled(False)  # 将该按钮设置为不可点击状态
        self.schedule.insideNumListen(whichelev, whichfloor)  # 调用控制器进行elevMove处理


    def connectDirListener(self):
        whichbtn = self.sender().objectName()
        if whichbtn[0] == 'd':#down
            choice = GODOWN
            whichfloor=int(whichbtn[7:])
        else:
            choice = GOUP
            whichfloor=int(whichbtn[5:])
        print("用户选择了 {0} {1}".format(whichfloor, choice))
        self.schedule.outsideDirListen(whichfloor, choice)  # 调用控制器进行chooseCtrl处理

