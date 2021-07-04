from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
from ElevatorUI import *
import numpy as np

import time, threading

INFINITE = 100

READY_UP = 1  # 用户要上行
READY_DOWN = 2  # 用户要下行

IS_OPEN = 0  # 开门状态
IS_CLOSED = 1  # 关门状态

STATIC = 0  # 静止状态
RUNNING_UP = 1  # 电梯上行状态
RUNNING_DOWN = 2  # 电梯下行状态

NONEANIM = 0  # 空动画
READY_START = 1  # 电梯即将运动
READY_STOP = 2  # 电梯即将停止

class MyScheduling(object):
    def __init__(self, UI):
        # 与界面文件建立连接
        self.elevators = UI

        # 500ms中更新一次电梯状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateElevState)
        self.timer.start(500)

        self.messQueue = [[] for i in range(0,5)]# 电梯内部消息列表
        self.messQueue_reverse = [[] for i in range(0,5)]

    # 开关按键监听
    def doorListen(self, whichelev, whichcommand):
        if whichcommand == 0:  # 开门
            if self.elevators.doorState[whichelev] == IS_CLOSED and self.elevators.elevState[whichelev] == STATIC:  # 如果当前门是关闭状态并且电梯是静止的
                self.elevators.doorState[whichelev] = IS_OPEN  # 先将门状态更新为打开
                self.elevators.elevEnabled[whichelev] = False
                self.doorAnim(whichelev,IS_OPEN)
        else:  # 关门
            if self.elevators.doorState[whichelev] == IS_OPEN and self.elevators.elevState[
                whichelev] == STATIC:  # 如果当前门是打开状态并且电梯是静止的
                self.elevators.doorState[whichelev] = IS_CLOSED  # 先将门状态更新为关闭
                self.elevators.elevEnabled[whichelev] = True
                self.doorAnim(whichelev,IS_CLOSED)

    # 电梯内部的数字按键监听(对消息列表处理)
    def insideNumListen(self, whichelev, dest):

        nowFloor = self.elevators.elevNow[whichelev]  # 获取当前电梯位置

        if nowFloor < dest:  # 如果按键大于当前楼层
            if self.elevators.elevState[whichelev] == STATIC:  # 电梯处于静止状态
                self.messQueue[whichelev].append(dest)  # 将目标楼层加入 消息队列

            else:
                if self.elevators.elevState[whichelev] == RUNNING_UP:  # 电梯正在向上运行
                    self.messQueue[whichelev].append(dest)  # 将目标楼层加入 消息队列并排序
                    self.messQueue[whichelev].sort()
                elif self.elevators.elevState[whichelev] == RUNNING_DOWN:  # 电梯正在向下运行
                    self.messQueue_reverse[whichelev].append(dest)  # 将目标楼层加入 不顺路消息队列并排序
                    self.messQueue_reverse[whichelev].sort()

        elif nowFloor > dest:
            if self.elevators.elevState[whichelev] == STATIC:
                self.messQueue[whichelev].append(dest)  # 将目标楼层加入 消息队列

            else:
                if self.elevators.elevState[whichelev] == RUNNING_DOWN:
                    self.messQueue[whichelev].append(dest)  # 将目标楼层加入 消息队列并反向排序
                    self.messQueue[whichelev].sort()
                    self.messQueue[whichelev].reverse()
                elif self.elevators.elevState[whichelev] == RUNNING_UP:
                    self.messQueue_reverse[whichelev].append(dest)  # 将目标楼层加入 不顺路消息队列并反向排序
                    self.messQueue_reverse[whichelev].sort()
                    self.messQueue_reverse[whichelev].reverse()

        else:  # 如果按键就为当前楼层
            if self.elevators.elevState[whichelev] == STATIC:  # 电梯静止 => 打开门(并等待用户自行关闭)
                self.elevators.doorState[whichelev] = IS_OPEN
                self.doorAnim(whichelev,IS_OPEN)
            button = self.elevators.findChild(QtWidgets.QPushButton,
                                         "button {0} {1}".format(whichelev, nowFloor))  # 恢复按键背景并重新允许点击
            button.setStyleSheet("")
            button.setEnabled(True)

    # 外部方向键监听(对消息列表处理)
    def outsideDirListen(self, whichfloor, choice):

        # region 选择没停用的电梯
        EnabledList = []
        for i in range(0, 5):
            if self.elevators.elevEnabled[i]:
                EnabledList.append(i)
        print(EnabledList)
        # endregion

        # region 计算每部可用电梯的"可调度性"
        dist = [INFINITE] * 5  # 可使用电梯距离用户的距离
        for EnabledElev in EnabledList:
            if self.elevators.elevState[EnabledElev] == RUNNING_UP and choice == READY_UP and whichfloor > self.elevators.elevNow[
                EnabledElev]:  # 向上顺路
                dist[EnabledElev] = whichfloor - self.elevators.elevNow[EnabledElev]

            elif self.elevators.elevState[EnabledElev] == RUNNING_DOWN and choice == READY_DOWN and whichfloor < \
                    self.elevators.elevNow[EnabledElev]:  # 向下顺路
                dist[EnabledElev] = self.elevators.elevNow[EnabledElev] - whichfloor

            elif self.elevators.elevState[EnabledElev] == STATIC:  # 该电梯此时静止
                dist[EnabledElev] = abs(self.elevators.elevNow[EnabledElev] - whichfloor)
        # endregion

        chooseElev = dist.index(min(dist))  # 选择可调度性最好的电梯作为最佳电梯
        if dist[chooseElev] == 0:  # 如果最佳电梯就在用户选择的楼层
            self.elevators.doorState[chooseElev] = IS_OPEN  # 打开门并等待用户自行关闭
            self.doorAnim(chooseElev, IS_OPEN)
        else:
            self.messQueue[chooseElev].append(whichfloor)  # 加入该最佳电梯的消息队列
            button = self.elevators.findChild(QtWidgets.QPushButton,
                                         "button {0} {1}".format(chooseElev, whichfloor))  # 将用户的目标楼层设定为特殊颜色
            button.setStyleSheet("background-color: rgb(11, 15, 255);")
            button.setEnabled(False)

    # 更新电梯状态
    def updateElevState(self):
        for i in range(0, len(self.messQueue)):  # 遍历五部电梯
            if len(self.messQueue[i]):  # 某个电梯的消息队列不为空

                if self.elevators.doorState[i] == IS_OPEN:  # 如果电梯门是打开的 => 等待电梯关门
                    continue

                elif self.elevators.elevState[i] == STATIC:  # 电梯处于静止状态
                    self.doorAnim(i,IS_OPEN)
                    self.pepoleAnim(i,IS_OPEN)
                    if self.elevators.elevNow[i] < self.messQueue[i][0]:  # 根据即将运行的方向更新电梯状态
                        self.elevators.elevState[i] = RUNNING_UP
                    elif self.elevators.elevNow[i] > self.messQueue[i][0]:
                        self.elevators.elevState[i] = RUNNING_DOWN

                    self.elevators.animState[i] = READY_START  # 动画变为就绪运行状态

                elif self.elevators.animState[i] == READY_START:  # 动画处于就绪运行状态
                    self.doorAnim(i,IS_CLOSED)
                    self.elevators.animState[i] = NONEANIM  # 动画变为空状态

                elif self.elevators.animState[i] == READY_STOP:  # 动画处于就绪停止状态
                    self.messQueue[i].pop(0)  # 结束该命令的处理
                    self.doorAnim(i,IS_CLOSED)
                    self.elevators.animState[i] = NONEANIM       # 动画变为空状态
                    self.elevators.elevState[i] = STATIC  # 电梯变为静止状态
                    self.elevators.stateshow[i].setStyleSheet("QGraphicsView{border-image: url(Resources/state.png)}")

                else:
                    destFloor = self.messQueue[i][0]  # 获取第一个目标楼层

                    if self.elevators.elevNow[i] < destFloor:  # 向上运动
                        self.elevators.elevState[i] = RUNNING_UP
                        self.elevators.stateshow[i].setStyleSheet(
                            "QGraphicsView{border-image: url(Resources/state_up.png)}")
                        self.elevators.elevNow[i] = self.elevators.elevNow[i] + 1  # 将当前楼层加一并设置数码管显示
                        self.elevators.lcdNumber[i].setProperty("value", self.elevators.elevNow[i])
                        self.elevators.elevator_label[i].setGeometry(QtCore.QRect((i + 1) * 40 + 900, 770 - 40 * (self.elevators.elevNow[i] - 1), 10, 35))

                        #电梯插入动画
                    elif self.elevators.elevNow[i] > destFloor:  # 向下运动
                        self.elevators.elevState[i] = RUNNING_DOWN
                        self.elevators.stateshow[i].setStyleSheet(
                            "QGraphicsView{border-image: url(Resources/state_down.png)}")
                        self.elevators.elevNow[i] = self.elevators.elevNow[i] - 1  # 将当前楼层减一并设置数码管显示
                        self.elevators.lcdNumber[i].setProperty("value", self.elevators.elevNow[i])
                        self.elevators.elevator_label[i].setGeometry(
                            QtCore.QRect((i + 1) * 40 + 900, 770 - 40 * (self.elevators.elevNow[i] - 1), 10, 35))
                    else:  # 电梯到达目的地
                        self.doorAnim(i,IS_OPEN)
                        self.pepoleAnim(i,IS_CLOSED)
                        self.elevators.animState[i] = READY_STOP  # 到达目的地 => 动画变为就绪停止状态

                        button = self.elevators.findChild(QtWidgets.QPushButton,
                                                     "button {0} {1}".format(i, self.elevators.elevNow[i]))  # 恢复该按钮的状态
                        button.setStyleSheet("")
                        button.setEnabled(True)

            elif len(self.messQueue_reverse[i]):  # 如果消息队列为空 & 不顺路消息队列不为空
                self.messQueue[i] = self.messQueue_reverse[i].copy()  # 交替两个队列
                self.messQueue_reverse[i].clear()

        # 电梯运行过程中禁止点击alarm键
        for i in range(0, 5):
            if self.elevators.gridLayoutWidget[i].isEnabled():  # 如果这个电梯没被禁用
                if self.elevators.elevState[i] == STATIC:  # 如果电梯是静止的
                    self.elevators.warnbtn[i].setEnabled(True)
                else:
                    self.elevators.warnbtn[i].setEnabled(False)

    # 禁用函数
    def stopUsingListen(self, whichelev):
        self.elevators.elevEnabled[whichelev] = False  # 该电梯禁用
        self.elevators.elevator_front[2 * whichelev + 1].setEnabled(False)  # 电梯前门禁用
        self.elevators.elevator_Anim[2 * whichelev].stop()  # 停止动画
        self.elevators.elevator_Anim[2 * whichelev + 1].stop()  # 停止动画
        self.elevators.label[whichelev].setEnabled(False)  # 电梯文字禁用
        self.elevators.lcdNumber[whichelev].setEnabled(False)  # 数码管禁用
        self.elevators.stateshow[whichelev].setEnabled(False)  # 上下行标志禁用
        self.elevators.warnbtn[whichelev].setEnabled(False)  # 报警键禁用
        self.elevators.gridLayoutWidget[whichelev].setEnabled(False)  # 楼层按键禁用
        self.elevators.openbtn[whichelev].setEnabled(False)  # 开门键禁用
        self.elevators.closebtn[whichelev].setEnabled(False)  # 关门键禁用
        self.elevators.elevator_back[whichelev].setEnabled(False)  # 电梯背景禁用
        self.elevators.elevator_front[2 * whichelev].setEnabled(False)  # 电梯前门禁用

        # 五部电梯全部禁用
        arr = np.array(self.elevators.elevEnabled)
        if ((arr == False).all()):
            self.elevators.comboBox.setEnabled(False)  # 下拉框禁用
            self.elevators.chooselabel.setEnabled(False)  # 文字禁用
            self.elevators.upbtn.setEnabled(False)  # 上行按钮禁用
            self.elevators.downbtn.setEnabled(False)  # 下行按钮禁用
            time.sleep(0.5)
            self.MessBox = QtWidgets.QMessageBox.information(self.elevators, "Warning", "All elevators are broken!")

    #门控动画
    def doorAnim(self,whichelev, doorState):
        if doorState==IS_OPEN:
            self.elevators.elevator_Anim[2 * whichelev].setDirection(QAbstractAnimation.Forward)  # 正向设定动画
            self.elevators.elevator_Anim[2 * whichelev + 1].setDirection(QAbstractAnimation.Forward)
        else:
            self.elevators.elevator_Anim[2 * whichelev].setDirection(QAbstractAnimation.Backward)  # 反向设定动画
            self.elevators.elevator_Anim[2 * whichelev + 1].setDirection(QAbstractAnimation.Backward)
        self.elevators.elevator_Anim[2 * whichelev].start()  # 开始播放
        self.elevators.elevator_Anim[2 * whichelev + 1].start()

    #人物动画
    def pepoleAnim(self,whichelev,doorState):
        self.elevators.figure[whichelev].setVisible(True)
        if doorState==0:
            self.elevators.figure_Anim[whichelev].setDirection(QAbstractAnimation.Forward)
            self.elevators.figure_Anim[whichelev].start()
            s = threading.Timer(1, self.setDoorTop, (whichelev,))  # 1秒之后把门至于顶层
            s.start()
        else:
            self.elevators.figure_Anim[whichelev].setDirection(QAbstractAnimation.Backward)
            self.elevators.figure_Anim[whichelev].start()
            s = threading.Timer(0.7, self.setPeopleTop, (whichelev,))  # 0.7s之后将人至于顶层
            s.start()
    # 将门至于顶层
    def setDoorTop(self, whichelev):
        self.elevators.elevator_front[2 * whichelev].raise_()
        self.elevators.elevator_front[2 * whichelev + 1].raise_()
    # 将小人至于顶层
    def setPeopleTop(self, whichelev):
        self.elevators.figure[whichelev].raise_()
        self.elevators.figure[whichelev].setVisible(False)






