from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import sys
from Cp134 import Ui_MainWindow
import serial
import serial.tools.list_ports
import datetime


# 程序界面初始化-
# 打开端口-
# 启动定时器并初始化读取串口子线程-读取到数据后将bytes信号发送到processdata函数，
# process在主线程中运行，界面数据更新完后，启动保存数据子线程
class MyMainWindow(QMainWindow, Ui_MainWindow):  # 继承 QMainWindow类和 Ui_MainWindow界面类
    def __init__(self, parent=None, ):
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
        self.data = None  # 用于存放每次从串口收到的
        self.data1 = None  # 用于存放每次下位机发送到的一个信息
        self.data2 = None
        self.data3 = None
        self.data4 = None
        self.data5 = None
        self.data6 = None
        self.progressBar.setValue(0)  # 关闭运行动画
        self.timer = None  # 对定时器进行定义，否则报错
        self.ferreshtime_timer = QTimer()  # 更新时间的定时器
        self.ferreshtime_timer.timeout.connect(self.update_current_time)
        self.ferreshtime_timer.start()

        self.lineEdit_Speedset.setValidator(QtGui.QIntValidator())  # 限制输入整数

    def Click_Button_Start(self):
        if self.ser:
            # 重新启动时的初始化操作
            self.progressBar.setValue(99)  # 开始运行动画
            self.pushButton_Start.setEnabled(False)
            self.pushButton_Stop.setEnabled(True)
            self.DataCount = 0  # 接收数据计数清零

            # 创建串口接收子线程并开启
            self.Thread_ReceiveData = Thread_ReceiveData(self.ser)
            self.Thread_ReceiveData.dataSignal.connect(self.ProsessData)
            self.timer = QTimer()  # 创建定时器开始定期接收
            self.timer.timeout.connect(self.Thread_ReceiveData.start)
            self.timer.start(100)  # 打开串口接收定时器，周期为5ms

    def Click_Button_Stop(self):
        self.progressBar.setValue(0)  # 关闭运行动画
        self.pushButton_Start.setEnabled(True)
        self.pushButton_Stop.setEnabled(False)
        if not self.ser:  # 如果端口已经关闭，不要激活启动按钮
            self.pushButton_Start.setEnabled(False)
        if self.timer:
            self.timer.stop()
        else:
            return

    def Click_Button_GetData(self):
        try:
            if self.ser:
                hex_str = 'FF03000000ED'
                # print(hex_str)
                self.ser.write(bytes.fromhex(hex_str))  # 文本框输入16进制字符串
                # self.statusBar.showMessage('获取传感器命令发送成功:' + hex_str, 500)

        except:
            QMessageBox.information(self, '端口错误', '发生异常')

    def update_current_time(self):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.label_RealTime.setText(current_time)

    # 功能函数
    def ProsessData(self, bytedata):
        self.data = bytedata  # 读取数据
        hex_data = ''.join([f'{byte:02X}' for byte in self.data])  # 将byte变量的值转换为两位的十六进制字符串（如果不足两位，则在前面补0）
        self.textBrowser.setText(hex_data)  # 在测试框中显示
        if self.data[0] == 0xff:  # 如果为有效数据
            #     # 每次接收到数据后的操作
            self.DataCount = self.DataCount + 1  # 计数值+1
            if self.data[1] == 0x01:
                self.statusBar.showMessage('接收到转速反馈命令:' + hex_data, 300)
            elif self.data[1] == 0x02:
                self.statusBar.showMessage('接收到阀门反馈命令:' + hex_data, 300)
            elif self.data[1] == 0x03:
                self.statusBar.showMessage('接收到下位机传感器反馈：' + hex_data, 300)
                self.data1 = int.from_bytes(self.data[2:4], byteorder='big', signed=False)  # 温度，2字节
                self.data2 = int.from_bytes(self.data[4:7], byteorder='big', signed=False)  # 气压1：3字节
                self.data3 = int.from_bytes(self.data[7:9], byteorder='big', signed=False)  # 流量：2字节
                self.data4 = int.from_bytes(self.data[9:11], byteorder='big', signed=False)  # 阀门角度：2字节
                # self.data5 = int.from_bytes(self.data[9:11], byteorder='big', signed=False)
                # self.data6 = int.from_bytes(self.data[11:13], byteorder='big', signed=False)
                self.lcdNumber_Data1.display(self.data1)  # 显示在数码管中
                self.lcdNumber_Data2.display(self.data2)
                self.lcdNumber_Data3.display(self.data3)
                self.lcdNumber_Data4.display(self.data4)
                # self.lcdNumber_Data5.display(self.data5)
        #     self.lcdNumber_Data6.display(self.data6)

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
                    # self.pushButton_TestConnect.setEnabled(True)
                    self.pushButton_TestConnect.setEnabled(False)
                    self.pushButton_CMD.setEnabled(True)
                    self.pushButton_SpeedsetSend.setEnabled(True)
                    # self.pushButton_MotorStop.setEnabled(True)
                    self.pushButton_MotorStop.setEnabled(False)
                    self.pushButton_MotorStart.setEnabled(True)
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
    # 转速给定发送
    def Click_Button_Speedset(self):
        try:
            if (self.ser) and self.lineEdit_Speedset.text():
                temp = int(self.lineEdit_Speedset.text())
                if (temp >= 0) and (temp <= 120000):
                    hex_str = 'FF01' + hex(temp)[2:].zfill(6) + 'ED'
                    print(hex_str)
                    self.ser.write(bytes.fromhex(hex_str))  # 文本框输入16进制字符串
                    self.statusBar.showMessage('发送成功,转速设定:' + str(temp), 500)
                    self.label_NowSpeed.setText(str(temp))

                else:
                    QMessageBox.information(self, '端口错误', '请确保转速给定输入为0-120000')
        except:
            QMessageBox.information(self, '端口错误', '发生异常')

    # 电机启动
    def Click_Button_MotorStart(self):
        try:
            if (self.ser) and self.lineEdit_Speedset.text():
                temp = int(self.lineEdit_Speedset.text())
                if (temp >= 0) and (temp <= 120000):
                    hex_str = 'FF01' + hex(temp)[2:].zfill(6) + 'ED'
                    print(hex_str)
                    self.ser.write(bytes.fromhex(hex_str))  # 文本框输入16进制字符串
                    self.statusBar.showMessage('发送成功,转速设定:' + str(temp), 500)
                    self.label_NowSpeed.setText(str(temp))

                else:
                    QMessageBox.information(self, '端口错误', '请确保转速给定输入为0-120000')
            else:
                self.statusBar.showMessage('请检查端口是否连接,请检查是否有输入', 500)
        except:
            QMessageBox.information(self, '端口错误', '发生异常')

    # 电机停止
    def Click_Button_MotorStop(self):
        try:
            if (self.ser):
                temp = 0
                if (temp >= 0) and (temp <= 120000):
                    hex_str = 'FF01' + hex(temp)[2:].zfill(6) + 'ED'
                    print(hex_str)
                    self.ser.write(bytes.fromhex(hex_str))  # 文本框输入16进制字符串
                    self.statusBar.showMessage('发送成功,转速设定:' + str(temp), 500)
                    self.label_NowSpeed.setText(str(temp))

                else:
                    QMessageBox.information(self, '端口错误', '请检查端口是否连接异常或检查输入')
        except:
            QMessageBox.information(self, '端口错误', '发生异常')


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
    app = QApplication(sys.argv)  # 在 QApplication 方法中使用，创建应用程序对象
    myWin = MyMainWindow()  # 实例化 MyMainWindow 类，创建主窗口
    myWin.show()  # 在桌面显示控件 myWin
    sys.exit(app.exec_())  # 结束进程，退出程序
