from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import sys
from PC_Controller_GUI_V2 import Ui_MainWindow
import serial
import serial.tools.list_ports
import queue
from queue import Queue
import pandas as pd
import os
import datetime
import time


# 几个时间相关
# self.timer.start(5)  # 打开串口接收定时器，周期为5ms
# self.ser = serial.Serial(port, baudrate, timeout=0.002)
# data_from_queue = self.data_queue.get(timeout=0.001)  # 从队列中获取数据，阻塞等待0.01s后抛出异常

# 程序界面初始化-
# 打开端口-
# 启动定时器并初始化读取串口子线程-读取到数据后将bytes信号发送到processdata函数，
# process在主线程中运行，界面数据更新完后，启动保存数据子线程
class MyMainWindow(QMainWindow, Ui_MainWindow):  # 继承 QMainWindow类和 Ui_MainWindow界面类
    def __init__(self, data_queue, parent=None, ):
        super(MyMainWindow, self).__init__(parent)  # 初始化父类

        self.setupUi(self)  # 继承 Ui_MainWindow 界面类
        self.Click_Button_RefreshCom()  # 程序运行时刷新端口
        self.ser = None  # 初始化串口
        self.label_ComTips.setStyleSheet('color: red')
        self.pushButton_CloseCom.setEnabled(False)  # 关闭端口按钮设置为禁用
        self.pushButton_Start.setEnabled(False)
        self.pushButton_Stop.setEnabled(False)
        self.pushButton_TestConnect.setEnabled(False)
        self.pushButton_CMD.setEnabled(False)
        self.pushButton_SpeedsetSend.setEnabled(False)
        self.pushButton_MotorStop.setEnabled(False)
        self.pushButton_MotorStart.setEnabled(False)
        self.pushButton_ValvesetSend.setEnabled(False)
        self.pushButton_ValveOpen.setEnabled(False)
        self.pushButton_ValveClose.setEnabled(False)
        self.data = None  # 用于存放每次从串口收到的
        self.data1 = None  # 用于存放每次下位机发送到的一个信息
        self.data2 = None
        self.data3 = None
        self.data4 = None
        self.data5 = None
        self.data6 = None
        self.data1_100 = []  # 用于存储100个数据
        self.data2_100 = []
        self.data3_100 = []
        self.data4_100 = []
        self.data5_100 = []
        self.data6_100 = []
        self.data1_all = []  # 用于存储全部个数据
        self.data2_all = []
        self.data3_all = []
        self.data4_all = []
        self.data5_all = []
        self.data6_all = []
        self.data_queue = data_queue  # 用于存储100个数据的队列
        self.plot1_data = self.graphicsView_1.plot()  # 初始化绘图1，方便后续直接用setdata绘图
        self.plot2_data = self.graphicsView_2.plot()
        self.comboBox_ChooseWave2.addItems(['Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6'])
        self.comboBox_ChooseWave1.addItems(['Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6'])
        self.DataCount = 0  # 计数值变量
        self.DataLists = []  # 存储100组6*1数据
        self.Point = 100  # 定点绘制波形初始点数
        self.progressBar.setValue(0)  # 关闭运行动画
        self.timer = None  # 对定时器进行定义，否则报错
        self.ferreshtime_timer = QTimer()  # 更新时间的定时器
        self.ferreshtime_timer.timeout.connect(self.update_current_time)
        self.ferreshtime_timer.start()
        self.tabWidget.setEnabled(False)

    def Click_Button_Start(self):
        if self.ser:
            # 重新启动时的初始化操作
            self.progressBar.setValue(99)  # 开始运行动画
            self.pushButton_Start.setEnabled(False)
            self.pushButton_Stop.setEnabled(True)
            self.data1_all = []  # 初始化大数组
            self.data2_all = []
            self.data3_all = []
            self.data4_all = []
            self.data5_all = []
            self.data6_all = []
            self.DataCount = 0  # 接收数据计数清零

            # 创建串口接收子线程并开启
            self.Thread_ReceiveData = Thread_ReceiveData(self.ser)
            self.Thread_ReceiveData.dataSignal.connect(self.ProsessData)
            self.timer = QTimer()  # 创建定时器开始定期接收
            self.timer.timeout.connect(self.Thread_ReceiveData.start)
            self.timer.start(5)  # 打开串口接收定时器，周期为1ms
            if self.checkBox_IfSave.isChecked():
                # # 创建数据保存子线程并开启定时器,取消注释时把closecom也取消注释
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')  # 启动时间时的时间
                self.Thread_SaveData = Thread_SaveData(self.data_queue, timestamp)  # 定义数据保存子线程
            self.checkBox_IfSave.setEnabled(False)  # 开始运行后不能点是否启用数据保存
            self.tabWidget.setEnabled(True)#点击start后才控制区才可操作
            self.elapsed_timelists = []
            self.start_time = datetime.datetime.now()  # 启动时间

    def Click_Button_Stop(self):
        self.progressBar.setValue(0)  # 关闭运行动画
        self.pushButton_Start.setEnabled(True)
        self.pushButton_Stop.setEnabled(False)
        self.checkBox_IfSave.setEnabled(True)  # 开始运行后不能点
        self.tabWidget.setEnabled(False)
        self.data_queue.queue.clear()
        if not self.ser:  # 如果端口已经关闭，不要激活启动按钮
            self.pushButton_Start.setEnabled(False)
        if self.timer:
            self.timer.stop()
        else:
            return

    def update_current_time(self):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.label_RealTime.setText(current_time)

    def slot_SetPoint(self):
        try:
            Point = int(self.lineEdit_PointChoose.text())
            if Point >= 100:
                self.Point = Point
            else:
                self.statusBar.showMessage('请输入大于100的整数', 1000)
                self.lineEdit_PointChoose.setText(str(100))
        except:
            self.statusBar.showMessage('请输入大于100的整数', 1000)
            self.lineEdit_PointChoose.setText(str(100))

    # 功能函数
    # 保存数据
    def save_data_thread(self):
        if not self.data_queue.empty():
            try:
                # 从队列中获取数据
                data_from_queue = self.data_queue.get(timeout=0.1)  # 0.1为阻塞等待时间，超处0.1会抛出异常
                # 将缓冲区中的数据转换成 DataFrame 格式，并写入到 Excel 文件中
                df = pd.DataFrame(data_from_queue, columns=self.columns)
                if not os.path.exists(self.file_path):
                    df.to_excel(self.file_path, index=False, columns=self.columns)
                    self.statusBar.showMessage('创建数据文件:' + self.file_path, 500)

                else:
                    with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl',
                                        if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
                        self.statusBar.showMessage('数据接收中···', 500)
            except queue.Empty:
                pass

    # 处理串口读取子线程返回的字节数据，在gui中更新数据、画图，并调用保存数据子线程
    def ProsessData(self, bytedata):
        self.data = bytedata  # 读取数据
        hex_data = ''.join([f'{byte:02X}' for byte in self.data])  # 将byte变量的值转换为两位的十六进制字符串（如果不足两位，则在前面补0）
        self.textBrowser.setText(hex_data)  # 在测试框中显示
        if self.data[0] == 0xff:  # 如果为有效数据
            # 每次接收到数据后的操作
            self.DataCount = self.DataCount + 1  # 计数值+1
            self.label_DataCount.setText(str(self.DataCount))
            self.data1 = int.from_bytes(self.data[1:3], byteorder='big', signed=False)  # 解析下位机数据并存储到对应变量中
            self.data2 = int.from_bytes(self.data[3:5], byteorder='big', signed=False)
            self.data3 = int.from_bytes(self.data[5:7], byteorder='big', signed=False)
            self.data4 = int.from_bytes(self.data[7:9], byteorder='big', signed=False)
            self.data5 = int.from_bytes(self.data[9:11], byteorder='big', signed=False)
            self.data6 = int.from_bytes(self.data[11:13], byteorder='big', signed=False)
            self.lcdNumber_Data1.display(self.data1)  # 显示在数码管中
            self.lcdNumber_Data2.display(self.data2)
            self.lcdNumber_Data3.display(self.data3)
            self.lcdNumber_Data4.display(self.data4)
            self.lcdNumber_Data5.display(self.data5)
            self.lcdNumber_Data6.display(self.data6)
            self.data1_100.append(self.data1)  # 将数据添加到存储100个数据的大列表中
            self.data2_100.append(self.data2)
            self.data3_100.append(self.data3)
            self.data4_100.append(self.data4)
            self.data5_100.append(self.data5)
            self.data6_100.append(self.data6)
            self.data1_all.append(self.data1)  # 将数据添加到存储所有数据的大列表中
            self.data2_all.append(self.data2)
            self.data3_all.append(self.data3)
            self.data4_all.append(self.data4)
            self.data5_all.append(self.data5)
            self.data6_all.append(self.data6)
            # 计算程序运行时间（秒）
            self.elapsed_timelists.append((datetime.datetime.now() - self.start_time).total_seconds())
            # 绘图
            # 波形1设置
            temp1 = self.comboBox_ChooseWave1.currentText()  # 获取combox中要显示波形的数据
            if self.radioButton_IfArealPlot1.isChecked():  # 如果选中的是顶点示图
                if temp1 == 'Data1':
                    self.plot1_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data1_all[-1 * self.Point:])
                elif temp1 == 'Data2':
                    self.plot1_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data2_all[-1 * self.Point:])
                elif temp1 == 'Data3':
                    self.plot1_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data3_all[-1 * self.Point:])
                elif temp1 == 'Data4':
                    self.plot1_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data4_all[-1 * self.Point:])
                elif temp1 == 'Data5':
                    self.plot1_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data5_all[-1 * self.Point:])
                elif temp1 == 'Data6':
                    self.plot1_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data6_all[-1 * self.Point:])
            elif self.radioButton_GlobalPlot1.isChecked():  # 如果选中的是全局示图
                if temp1 == 'Data1':
                    self.plot1_data.setData(x=self.elapsed_timelists, y=self.data1_all)
                elif temp1 == 'Data2':
                    self.plot1_data.setData(x=self.elapsed_timelists, y=self.data2_all)
                elif temp1 == 'Data3':
                    self.plot1_data.setData(x=self.elapsed_timelists, y=self.data3_all)
                elif temp1 == 'Data4':
                    self.plot1_data.setData(x=self.elapsed_timelists, y=self.data4_all)
                elif temp1 == 'Data5':
                    self.plot1_data.setData(x=self.elapsed_timelists, y=self.data5_all)
                elif temp1 == 'Data6':
                    self.plot1_data.setData(x=self.elapsed_timelists, y=self.data6_all)
            # 波形2配置
            temp2 = self.comboBox_ChooseWave2.currentText()
            if self.radioButton_IfArealPlot2.isChecked():  # 如果选中的是顶点示图
                if temp2 == 'Data1':
                    self.plot2_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data1_all[-1 * self.Point:])
                elif temp2 == 'Data2':
                    self.plot2_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data2_all[-1 * self.Point:])
                elif temp2 == 'Data3':
                    self.plot2_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data3_all[-1 * self.Point:])
                elif temp2 == 'Data4':
                    self.plot2_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data4_all[-1 * self.Point:])
                elif temp2 == 'Data5':
                    self.plot2_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data5_all[-1 * self.Point:])
                elif temp2 == 'Data6':
                    self.plot2_data.setData(x=self.elapsed_timelists[-1 * self.Point:],
                                            y=self.data6_all[-1 * self.Point:])
            elif self.radioButton_GlobalPlot2.isChecked():  # 如果选中的是全局示图
                if temp2 == 'Data1':
                    self.plot2_data.setData(x=self.elapsed_timelists, y=self.data1_all)
                elif temp2 == 'Data2':
                    self.plot2_data.setData(x=self.elapsed_timelists, y=self.data2_all)
                elif temp2 == 'Data3':
                    self.plot2_data.setData(x=self.elapsed_timelists, y=self.data3_all)
                elif temp2 == 'Data4':
                    self.plot2_data.setData(x=self.elapsed_timelists, y=self.data4_all)
                elif temp2 == 'Data5':
                    self.plot2_data.setData(x=self.elapsed_timelists, y=self.data5_all)
                elif temp2 == 'Data6':
                    self.plot2_data.setData(x=self.elapsed_timelists, y=self.data6_all)

            # 暂时性保存数据
            templist = []  # 拼接一组数据
            time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            templist = [time_str, str(self.data1), str(self.data2), str(self.data3), str(self.data4), str(self.data5),
                        str(self.data6)]
            self.DataLists.append(templist)  # 将拼接好的一组数据添加到大数组中

            # 接收到200组数据后的操作：放入队列并调用子线程
            if len(self.DataLists) == 100:
                if self.checkBox_IfSave.isChecked and self.Thread_SaveData:
                    self.data_queue.put(list(self.DataLists))
                    self.Thread_SaveData.start()  # 方式一：多线程保存
                self.DataLists.clear()  # 清空

            else:
                return

    # ****************************下位机连接******************************
    # 打开端口
    def Click_Button_OpenCom(self):
        baudrate = int(self.BaudChoose.currentText())  # 波特率
        port = self.ComChoose.currentText()  # 端口号
        try:
            if not port:
                QMessageBox.information(self, '端口配置错误', '请选择端口！')
                return
            if (port) and (baudrate):
                try:
                    self.ser = serial.Serial(port, baudrate, timeout=0.002)
                    self.ser.flushInput()  # 清除缓冲数据
                    self.ser.flushOutput()
                    self.statusBar.showMessage('端口连接成功', 1000)
                    self.label_ComTips.setText("[端口已打开]")
                    self.label_ComTips.setStyleSheet('color: green')
                    self.ComChoose.setEnabled(False)  # 串口号和波特率变为不可选择
                    self.BaudChoose.setEnabled(False)
                    self.pushButton_OpenCom.setEnabled(False)
                    self.pushButton_CloseCom.setEnabled(True)
                    self.pushButton_Start.setEnabled(True)
                    self.pushButton_TestConnect.setEnabled(True)
                    self.pushButton_CMD.setEnabled(True)
                    self.pushButton_SpeedsetSend.setEnabled(True)
                    self.pushButton_MotorStop.setEnabled(True)
                    self.pushButton_MotorStart.setEnabled(True)
                    self.pushButton_ValvesetSend.setEnabled(True)
                    self.pushButton_ValveOpen.setEnabled(True)
                    self.pushButton_ValveClose.setEnabled(True)

                except serial.SerialException as e:
                    QMessageBox.information(self, '端口配置错误', f'打开端口失败：{e}')
        except serial.SerialException as e:
            QMessageBox.information(self, '端口配置错误', f'打开端口失败：{e}')

    # 关闭端口
    def Click_Button_CloseCom(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.ComChoose.setEnabled(True)  # 串口号和波特率变为不可选择
            self.BaudChoose.setEnabled(True)
            self.statusBar.showMessage('端口已关闭', 1000)
            self.label_ComTips.setText("[端口已关闭]")
            self.label_ComTips.setStyleSheet('color: red')
            self.pushButton_OpenCom.setEnabled(True)
            self.pushButton_CloseCom.setEnabled(False)
            self.pushButton_Start.setEnabled(False)
            self.pushButton_Stop.setEnabled(False)
            self.pushButton_TestConnect.setEnabled(False)
            self.pushButton_CMD.setEnabled(False)
            self.pushButton_SpeedsetSend.setEnabled(False)
            self.pushButton_MotorStop.setEnabled(False)
            self.pushButton_MotorStart.setEnabled(False)
            self.pushButton_ValvesetSend.setEnabled(False)
            self.pushButton_ValveOpen.setEnabled(False)
            self.pushButton_ValveClose.setEnabled(False)
            self.Click_Button_Stop()  # 断开端口时要停止运行

    # 刷新端口
    def Click_Button_RefreshCom(self):
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        self.ComChoose.clear()
        self.ComChoose.addItems(self.ports)  # 将端口添加到combox中
        self.statusBar.showMessage('端口刷新成功，检测到端口:' + "".join(self.ports), 2000)

    # 测试连接
    def Click_Button_TestConnect(self):
        # self.statusBar.showMessage('端口刷新成功，检测到端口:' + "".join(self.ports), 2000)
        # self.lcdNumber_Data1.setEnabled(True)

        pass

    # 发送     hex（255）=”0xff“  [2:]：去除转换后的字符串中的前缀 '0x'，例如将 '0xff' 转换为 'ff'
    #              #  zfill(4)：在字符串的左侧填充零，使得字符串的长度达到 4 位，例如将 'ff' 转换为 '00ff'。
    def Click_Button_Send(self):
        try:
            if (self.ser) and self.lineEdit.text():
                self.ser.write(bytes.fromhex(self.lineEdit.text()))  # 文本框输入16进制字符串
                self.statusBar.showMessage('发送成功', 500)
                return
        except:
            QMessageBox.information(self, '端口错误', '请确保输入为完整的16进制，0-f，个数为2的N倍')

    # ****************************下位机控制******************************
    #*******************开环模式
    # 转速给定发送
    def Click_Button_Speedset(self):  # 点击 pushButton_2 触发
        # self.label_Data1.setText('按钮1点击成功')
        self.lcdNumber_Data1.display(99999)
        return

    # 电机启动
    def Click_Button_MotorStart(self):
        sendstr = 'ff01'
        try:
            if (self.ser) and self.lineEdit.text():
                self.ser.write(bytes.fromhex(self.lineEdit.text()))  # 文本框输入16进制字符串
                self.statusBar.showMessage('发送成功', 500)
                return
        except:
            QMessageBox.information(self, '端口错误', '请确保输入为完整的16进制，0-f，个数为2的N倍')
        pass

    # 电机停止
    def Click_Button_MotorStop(self):
        pass
    #电机故障重置
    def Click_Button_MotroReset(self):
        pass
        return

    # 阀门全开
    def Click_Button_VlaveAllOpen(self):
        pass

    # 阀门全关
    def Click_Button_ValveAllClose(self):
        pass

    # 阀门给定发送
    def Click_Button_Valveset(self):  # 点击 pushButton_2 触发
        self.lcdNumber_Data2.display(123.4)
        return
    #*******************闭环模式*************************************
    def Click_Button_CloLp_subbmit(self):
        pass
    def Click_Button_CloLp_start(self):
        pass
    def Click_Button_CloLp_stop(self):
        pass
    def Click_Button_CloLp_reset(self):
        pass


# 定义保存数据子线程
class Thread_SaveData(QThread):
    def __init__(self, data_queue, timestamp):
        super().__init__()  ## 继承QThread
        self.data_queue = data_queue  # queue对象
        # self.file_path = 'DATA_' + timestamp + '.xlsx'  # 按照打开软件时的时间创建文件
        self.file_path = 'DATA_' + timestamp + '.csv'  # 按照打开软件时的时间创建文件
        self.columns = ['Time', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6']  # 用于创建文件时的标题头
        self.start_row = 0  # 用于跟踪已经写入的行数

    def run(self):
        if not self.data_queue.empty():
            try:
                # start_time = time.time()  # 测试运行
                # print(self.data_queue.qsize())
                data_from_queue = self.data_queue.get(timeout=0.001)  # 从队列中获取数据，阻塞等待0.01s后抛出异常
                df = pd.DataFrame(data_from_queue, columns=self.columns)

# *************************************excel写入*******************************
#                 if not os.path.exists(self.file_path):  # 检测有无文件，没有的话根据实例化的时间创建一个
#                     df.to_excel(self.file_path, index=False, columns=self.columns)
#                     self.start_row += 1
#                     # self.statusBar.showMessage('创建数据文件:' + self.file_path,500)
#                 # ***********************以上代码运行时间1ms，初次创建文件需要30ms
#                 with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl',
#                                     if_sheet_exists='overlay') as writer:
#                     # ***********************以上代码运行时间30ms-50ms，比较稳定
#                     start_time = time.time()  # 测试运行
#                     df.to_excel(writer, index=False, header=False, startrow=self.start_row)
#                     self.start_row += len(df)
#                 end_time = time.time()
#                 execution_time = end_time - start_time
#                 print("程序运行时间：", execution_time, "秒")
# *************************************csv写入*******************************

                if not os.path.exists(self.file_path):
                    df.to_csv(self.file_path, index=False, columns=self.columns)#创建csv文件，并写入列名

                with open(self.file_path, 'a',newline='') as file:
                    df.to_csv(file, index=False, header=False)# header=False: 防止写入 CSV 文件时写入列名（因为已经在文件开头写入过一次了）。
                # end_time = time.time()
                # execution_time = end_time - start_time
                # print("程序运行时间：", execution_time, "秒")

            except queue.Empty:
                pass


# 接收串口数据子线程
class Thread_ReceiveData(QThread):
    dataSignal = pyqtSignal(bytes)  # 定义一个信号，用于传输数据

    def __init__(self, ser):
        super().__init__()  ## 继承QThread
        self.ser = ser

    def run(self):
        if self.ser and self.ser.isOpen:
            num = self.ser.inWaiting()
            if num > 0:  # 串口缓冲区有数据的话
                data = self.ser.read_all()  # 读取数据
                self.dataSignal.emit(data)  # 发送读取回来的字节信号
        else:
            return


if __name__ == '__main__':
    data_queue = Queue()  # 定义全局队列对象
    app = QApplication(sys.argv)  # 在 QApplication 方法中使用，创建应用程序对象
    myWin = MyMainWindow(data_queue)  # 实例化 MyMainWindow 类，创建主窗口
    myWin.show()  # 在桌面显示控件 myWin
    sys.exit(app.exec_())  # 结束进程，退出程序
