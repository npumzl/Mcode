import os
import queue
import sys
import threading
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import datetime
import pandas as pd
from queue import Queue
from tkinter import messagebox


# 主窗口
class SerialAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PEMFC空气供应系统上位机V1.0")

        # 初始化
        self.line1 = None  # 曲线1
        self.line2 = None  # 曲线2
        self.line3 = None  # 曲线3
        self.line4 = None  # 曲线4
        self.data1 = None
        self.data2 = None
        self.data3 = None
        self.data4 = None
        self.data5 = None
        self.data6 = None
        self.data1_list = []
        self.data2_list = []
        self.data3_list = []
        self.data4_list = []
        self.data5_list = []
        self.data6_list = []

        # 初始化串口参数
        self.ser = None
        self.baudrate_var = tk.StringVar(self)
        self.port_var = tk.StringVar(self)

        # 创建界面控件
        self.create_serial_frame()
        self.create_command_frame()
        self.create_data_frame()  # 创建数据显示框
        self.create_datashow_frame()
        self.create_monitor_frame()
        self.create_state_frame()
        self.state.set('请配置端口···')

        # 数据保存
        self.databuffer = []
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.file_path = 'received_data_' + timestamp + '.xlsx'
        self.columns = ['time', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6']  # Excel表格列名
        self.data_queue = Queue()

    # 创建串口设置区域
    def create_serial_frame(self):
        serial_frame = tk.LabelFrame(self, text="端口配置", padx=10, pady=10, font=('微软雅黑', 15, "bold"))
        serial_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N, padx=10, pady=5)

        # 串口列表下拉菜单
        ports_label = ttk.Label(serial_frame, text="端口选择:", font=('微软雅黑', 12))
        ports_label.grid(row=0, column=0, sticky=tk.W)
        self.ports_combobox = ttk.Combobox(serial_frame, textvariable=self.port_var, width=10)
        self.ports_combobox.grid(row=0, column=1, sticky=tk.W)
        self.populate_ports_combobox()

        # 波特率下拉菜单
        baudrate_label = ttk.Label(serial_frame, text="波特率:", font=('微软雅黑', 12))
        baudrate_label.grid(row=1, column=0, sticky=tk.W)
        baudrate_combobox = ttk.Combobox(serial_frame, textvariable=self.baudrate_var, width=10)
        baudrate_combobox.grid(row=1, column=1, sticky=tk.W)
        baudrate_combobox['values'] = [
            '2400',
            '4800',
            '9600',
            '14400',
            '19200',
            '38400',
            '57600',
            '115200'
        ]
        baudrate_combobox.current(7)
        # 打开串口按钮
        style = ttk.Style()
        style.configure("TButton", font=('微软雅黑', 12))
        open_button = ttk.Button(serial_frame, style="TButton", text="打开端口", command=self.open_serial_port)
        open_button.grid(row=3, column=0, pady=10, padx=5)

        # 关闭串口按钮
        close_button = ttk.Button(serial_frame, text="关闭端口", command=self.close_serial_port)
        close_button.grid(row=3, column=1, padx=5)

        # 刷新串口列表按钮
        refresh_button = ttk.Button(serial_frame, text="刷新端口", command=self.refresh_ports_list, width=8)
        refresh_button.grid(row=3, column=2, padx=5)

        # 连接状态标签
        self.connection_status_label = ttk.Label(serial_frame, text="Connection Status: Not Connected",
                                                 foreground='red', font=("Arial", 10, "bold"), )
        self.connection_status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W)

    # 刷新串口列表
    def refresh_ports_list(self):
        self.populate_ports_combobox()
        self.state.set('端口刷新成功！')

    # 创建命令发送区域
    def create_command_frame(self):
        command_frame = tk.LabelFrame(self, text="命令给定", font=('微软雅黑', 15, "bold"), padx=10, pady=10)
        command_frame.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N, padx=10, pady=5, ipadx=0)

        # 两个命令输入框和发送按钮
        speed_label = ttk.Label(command_frame, text='转速给定：', font=('微软雅黑', 12))
        speed_label.grid(row=0, column=0)
        self.command_entry1 = ttk.Entry(command_frame, width=14, font=('Times New Roman', 15))
        self.command_entry1.grid(row=0, column=1, sticky=tk.W, padx=5)
        send_button1 = ttk.Button(command_frame, text="命令发送", command=self.send_command1, width=8)
        send_button1.grid(row=0, column=2)

        angle_label = ttk.Label(command_frame, text='阀门给定：', font=('微软雅黑', 12))
        angle_label.grid(row=1, column=0)
        self.command_entry2 = ttk.Entry(command_frame, width=14, font=('Times New Roman', 15))
        self.command_entry2.grid(row=1, column=1, sticky=tk.W, padx=5)
        send_button2 = ttk.Button(command_frame, text="命令发送", command=self.send_command2, width=8)
        send_button2.grid(row=1, column=2)

        # 命令状态标签
        self.cmd_status_label = ttk.Label(command_frame, text="命令提示：", foreground='black', font=('微软雅黑', 12))
        self.cmd_status_label.grid(row=3, column=0, columnspan=3, sticky=tk.W)

    # 创建发送和接收数据显示框
    def create_data_frame(self):
        data_frame = tk.LabelFrame(self, text="数据显示", padx=10, pady=5, font=('微软雅黑', 15, "bold"))
        data_frame.grid(row=2, column=0, sticky=tk.W + tk.E + tk.N, padx=10, pady=5)

        # 发送数据显示框
        self.send_data = tk.StringVar()
        send_label = ttk.Label(data_frame, text='发送数据：', font=('微软雅黑', 12))
        send_label.grid(row=0, column=0, pady=5)
        send_data_label = tk.Label(data_frame, width=32, textvariable=self.send_data, relief="sunken", )  # 高度设置为1行
        send_data_label.grid(row=0, column=1, sticky=tk.W)

        # 接收数据显示框
        self.receiver_data = tk.StringVar()
        receive_label = ttk.Label(data_frame, text='接收数据：', font=('微软雅黑', 12))
        receive_label.grid(row=1, column=0, pady=5)
        receive_data_label = tk.Label(data_frame, width=32, textvariable=self.receiver_data, relief="sunken")  # 高度设置为1行
        receive_data_label.grid(row=1, column=1, sticky=tk.W)

    # 自动检测串口并填充下拉菜单
    def populate_ports_combobox(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.ports_combobox["values"] = ports

    # 打开串口
    def open_serial_port(self):
        port = self.port_var.get()
        baudrate = int(self.baudrate_var.get())
        try:
            if self.ser and self.ser.is_open:
                # 端口已经打开
                messagebox.showwarning('Warnning', '端口已打开！')
            else:
                if not port:
                    # 没有选择端口
                    messagebox.showwarning('Warnning', '请选择端口！')
                else:
                    self.ser = serial.Serial(port, baudrate, timeout=0.002)
                    self.ser.flushInput()  # 清除缓冲数据
                    self.ser.flushOutput()
                    self.connection_status_label.config(text="Connection Status: Connected", foreground='green')
                    self.state.set('端口打开成功，开始接收数据···')
        except serial.SerialException as e:
            messagebox.showwarning('Warnning', f'打开端口失败：{e}')

    # 关闭串口
    def close_serial_port(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.connection_status_label.config(text="Connection Status: Not Connected", foreground='red')
            self.state.set('端口已关闭···')
        else:
            messagebox.showwarning('Warnning', '当前所选端口已关闭！')

    # 发送命令1
    def send_command1(self):
        try:
            command_int = int(self.command_entry1.get())
            command_int = int(command_int / 120000 * 65535)  # 转速范围0-12W
            hex_str = 'FF01' + hex(command_int)[2:].zfill(4) + 'ED'
            if self.ser:
                self.ser.write(bytes.fromhex(hex_str))
                self.send_data.set(hex_str)
                self.cmd_status_label.config(text=f"CMD1发送成功···", foreground='green')
                self.state.set('CMD1发送成功:' + hex_str)
            else:
                self.cmd_status_label.config(text=f"请检查端口是否连接！", foreground='red')
        except:
            self.cmd_status_label.config(text=f"请检查CMD1数据有效性！", foreground='red')

    # 发送命令2
    def send_command2(self):
        try:
            command_int = int(self.command_entry2.get())
            hex_str = 'ff02' + hex(command_int)[2:].zfill(4) + 'ed'
            if self.ser:
                self.ser.write(bytes.fromhex(hex_str))
                self.send_data.set(hex_str)
                self.cmd_status_label.config(text=f"CMD2发送成功···", foreground='green')
                self.state.set('CMD2发送成功:' + hex_str)
            else:
                self.cmd_status_label.config(text=f"请检查端口是否连接！", foreground='red')
        except:
            self.cmd_status_label.config(text=f"请检查CMD2数据有效性！", foreground='red')

    # 接收数据
    def receive_data(self):
        if self.ser:
            self.data = self.ser.read_all()
            # 若为有效数据
            if self.data:
                # 上位机显示数据
                hex_data = ''.join([f'{byte:02X}' for byte in self.data])
                self.receiver_data.set(hex_data)
                if (self.data[0] == 0xff):
                    self.data1.set(int.from_bytes(self.data[1:3], byteorder='big', signed=False))
                    self.data2.set(int.from_bytes(self.data[3:5], byteorder='big', signed=False))
                    self.data3.set(int.from_bytes(self.data[5:7], byteorder='big', signed=False))
                    self.data4.set(int.from_bytes(self.data[7:9], byteorder='big', signed=False))
                    self.data5.set(int.from_bytes(self.data[9:11], byteorder='big', signed=False))
                    self.data6.set(int.from_bytes(self.data[11:13], byteorder='big', signed=False))

                # 添加时间和所有数据到一个临时列表中
                time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_list = [time_str]
                for i in range(6):
                    data_list.append(str(eval(f'self.data{i + 1}.get()')))
                self.databuffer.append(data_list)

                # 以data1为计数，用于计数有效数据个数
                self.count_datalists.append(self.data1.get())
                self.data_count.set(len(self.count_datalists))

                # 每100次将数据放到队列中
                if len(self.databuffer) == 100:
                    if self.execute_flag.get():
                        self.data_queue.put(list(self.databuffer))
                        self.update_plot()
                    self.databuffer.clear()  # 缓冲区满100后，清空缓冲区

        self.after(10, self.receive_data)  # 每20毫秒读取一次串口数据

    # 保存数据的线程函数
    def save_data_thread(self):
        while True:
            if not self.data_queue.empty():
                try:
                    # 从队列中获取数据
                    data_from_queue = self.data_queue.get(timeout=1)
                    # 将缓冲区中的数据转换成 DataFrame 格式，并写入到 Excel 文件中
                    df = pd.DataFrame(data_from_queue, columns=self.columns)
                    if not os.path.exists(self.file_path):
                        df.to_excel(self.file_path, index=False, columns=self.columns)
                        self.state.set('创建数据文件:' + self.file_path)
                    else:
                        with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl',
                                            if_sheet_exists='overlay') as writer:
                            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
                            self.state.set('创建数据文件:' + self.file_path + "  数据接收中···")
                except queue.Empty:
                    pass
            time.sleep(0.01)
        pass

    def update_plot(self):
        if self.ser and self.data:
            try:
                self.data1_list.append(self.data1.get())
                self.data2_list.append(self.data2.get())
                self.data3_list.append(self.data3.get())
                self.data4_list.append(self.data4.get())
                self.data5_list.append(self.data5.get())
                self.data6_list.append(self.data6.get())
                # 更新子图数据
                self.on_combobox1_change(None)
                self.on_combobox2_change(None)
                self.on_combobox3_change(None)
                self.on_combobox4_change(None)
            except serial.SerialException as e:
                self.connection_status_label.config(text=f"{e}", foreground='red')
        # self.after(100, self.update_plot)

    def on_combobox_change(self, event, comboBox, ax, data_dict):
        selected_option = comboBox.get()
        if selected_option == 'None':
            ax.clear()
        else:
            ax.clear()
            data = data_dict[selected_option]
            ax.plot(list(range(len(data))), data, 'r-', label=selected_option)
            ax.legend()
            ax.set_title(selected_option)
        self.canvas.draw()

    def on_combobox1_change(self, event):
        comboBox = self.comboBox1
        ax = self.ax1
        data_dict = {
            'Data1': self.data1_list,
            'Data2': self.data2_list,
            'Data3': self.data3_list,
            'Data4': self.data4_list,
            'Data5': self.data5_list,
            'Data6': self.data6_list
        }
        self.on_combobox_change(event, comboBox, ax, data_dict)

    def on_combobox2_change(self, event):
        comboBox = self.comboBox2
        ax = self.ax2
        data_dict = {
            'Data1': self.data1_list,
            'Data2': self.data2_list,
            'Data3': self.data3_list,
            'Data4': self.data4_list,
            'Data5': self.data5_list,
            'Data6': self.data6_list
        }
        self.on_combobox_change(event, comboBox, ax, data_dict)

    def on_combobox3_change(self, event):
        comboBox = self.comboBox3
        ax = self.ax3
        data_dict = {
            'Data1': self.data1_list,
            'Data2': self.data2_list,
            'Data3': self.data3_list,
            'Data4': self.data4_list,
            'Data5': self.data5_list,
            'Data6': self.data6_list
        }
        self.on_combobox_change(event, comboBox, ax, data_dict)

    def on_combobox4_change(self, event):
        comboBox = self.comboBox4
        ax = self.ax4
        data_dict = {
            'Data1': self.data1_list,
            'Data2': self.data2_list,
            'Data3': self.data3_list,
            'Data4': self.data4_list,
            'Data5': self.data5_list,
            'Data6': self.data6_list
        }
        self.on_combobox_change(event, comboBox, ax, data_dict)

    # 启动串口数据接收
    def start_receive_save_plot_data(self):
        self.after(50, self.receive_data)
        # self.after(100, self.update_plot)
        # 多线程实现数据保存
        save_thread = threading.Thread(target=self.save_data_thread)
        save_thread.start()
        # self.receive_thread = threading.Thread(target=self.receive_data)
        # self.receive_thread.start()
        # self.plot_thread = threading.Thread(target=self.update_plot)
        # self.plot_thread.start()

    def create_datashow_frame(self):
        datashow_frame = tk.LabelFrame(self, text="数据监测", padx=10, pady=10, font=('微软雅黑', 15, "bold"))
        datashow_frame.grid(row=3, column=0, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=5)
        # 数据显示
        self.data = []  # 接收到的所有数据字节
        self.xdata = []  # 画图的横坐标数据
        self.count_datalists = []
        self.data_list = [self.data1_list, self.data2_list, self.data3_list, self.data4_list, self.data5_list,
                          self.data6_list]

        for i in range(6):
            data_var = tk.IntVar()
            data_label = ttk.Label(datashow_frame, text=f"数据{i + 1}:", font=('微软雅黑', 12))
            data_label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            data_entry = tk.Entry(datashow_frame, width=10, textvariable=data_var, justify=tk.RIGHT,
                                  font=('Times New Roman', 12))
            data_entry.grid(row=i, column=1)
            setattr(self, f"data{i + 1}", data_var)
            setattr(self, f"data{i + 1}_entry", data_entry)

    def update_current_time(self):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.current_time_label.config(text=current_time)
        self.after(1000, self.update_current_time)  # 每隔1秒更新一次时间

    # 创建数据显示区域
    def create_monitor_frame(self):
        monitor_frame = tk.LabelFrame(self, text="数据监测", padx=10, pady=5, font=('微软雅黑', 15, "bold"))
        monitor_frame.grid(row=0, column=1, sticky=tk.W + tk.N + tk.S, padx=5, pady=5, rowspan=4)

        # 当前时间日期标签
        self.current_time_label = ttk.Label(monitor_frame, text="", font=('Times New Roman', 12))
        self.current_time_label.grid(row=0, column=0, sticky=tk.E + tk.N, pady=0)
        # 更新当前时间日期
        self.update_current_time()

        # 接收数据计数显示
        self.data_count = tk.IntVar()
        datacount_label = ttk.Label(monitor_frame, text='接收数据计数：', font=('微软雅黑', 12))
        datacount_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        ydata_count = ttk.Label(monitor_frame, textvariable=self.data_count, font=('Arial', 12))
        ydata_count.grid(row=0, column=0, sticky=tk.W, padx=110)

        # 创建两个下拉框控件
        style = ttk.Style()
        style.configure("TCombobox", font=('微软雅黑', 12))
        choices = ['None', "Data1", "Data2", "Data3", "Data4", "Data5", "Data6"]
        self.comboBox1 = ttk.Combobox(monitor_frame, values=choices, style="TCombobox", width=6)
        self.comboBox2 = ttk.Combobox(monitor_frame, values=choices, style="TCombobox", width=6)
        self.comboBox3 = ttk.Combobox(monitor_frame, values=choices, style="TCombobox", width=6)
        self.comboBox4 = ttk.Combobox(monitor_frame, values=choices, style="TCombobox", width=6)

        # 设置默认选中的选项
        self.comboBox1.current(0)
        self.comboBox2.current(0)
        self.comboBox3.current(0)
        self.comboBox4.current(0)

        # 在界面上将下拉框放置到合适的位置
        ttk.Label(monitor_frame, text="图1", font=('微软雅黑', 12)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.comboBox1.grid(row=1, column=0, sticky=tk.W, padx=40, pady=5)
        ttk.Label(monitor_frame, text="图2", font=('微软雅黑', 12)).grid(row=1, column=0, sticky=tk.W, padx=115)
        self.comboBox2.grid(row=1, column=0, sticky=tk.W, padx=150, pady=5)
        ttk.Label(monitor_frame, text="图3", font=('微软雅黑', 12)).grid(row=1, column=0, sticky=tk.W, padx=225)
        self.comboBox3.grid(row=1, column=0, sticky=tk.W, padx=260, pady=5)
        ttk.Label(monitor_frame, text="图4", font=('微软雅黑', 12)).grid(row=1, column=0, sticky=tk.W, padx=335)
        self.comboBox4.grid(row=1, column=0, sticky=tk.W, padx=370, pady=5)

        # 绑定下拉框事件
        self.comboBox1.bind("<<ComboboxSelected>>", self.on_combobox1_change)
        self.comboBox2.bind("<<ComboboxSelected>>", self.on_combobox2_change)
        self.comboBox3.bind("<<ComboboxSelected>>", self.on_combobox3_change)
        self.comboBox4.bind("<<ComboboxSelected>>", self.on_combobox4_change)

        self.execute_flag = tk.BooleanVar(value=False)
        # 创建勾选框
        checkbutton = tk.Checkbutton(monitor_frame, text='绘制图像', font=('微软雅黑', 12), variable=self.execute_flag)
        checkbutton.grid(row=1, column=0, sticky=tk.E)

        # 创建图形窗口
        self.fig = plt.figure(figsize=(12, 12), dpi=70)
        # 调整子图位置和间距
        self.fig.subplots_adjust(top=0.95, bottom=0.1, left=0.05, right=0.95, hspace=0.4, wspace=0.2)

        # 创建六个子图对象
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)

        # 设置子图的标题和轴标签
        titles = ['Data1', 'Data2', 'Data3', 'Data4']
        axes = [self.ax1, self.ax2, self.ax3, self.ax4]
        for i in range(len(titles)):
            axes[i].set_title(titles[i])
            axes[i].set_xlabel('X')
            axes[i].set_ylabel('Y')
            axes[i].grid(True)

        # 绘制数据曲线并设置标签和样式
        lines = [self.line1, self.line2, self.line3, self.line4]
        data_lists = [self.data1_list, self.data2_list, self.data3_list, self.data4_list]
        colors = ['r-', 'b-', 'g-', 'c-']
        for i in range(len(lines)):
            lines[i], = axes[i].plot(self.xdata, data_lists[i], colors[i], label=titles[i])

        # 使用grid方法排列子图
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.ax3.grid(True)
        self.ax4.grid(True)

        # 将图形绘制到canvas上，并显示在窗口中
        self.canvas = FigureCanvasTkAgg(self.fig, master=monitor_frame)
        self.canvas.get_tk_widget().config(width=800, height=600, bg='yellow')
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=1, sticky=tk.W + tk.S, padx=5, pady=5)

    def create_state_frame(self):
        status_frame = tk.LabelFrame(self, text="上位机运行状态监测", padx=5, pady=10, font=('微软雅黑', 10))
        status_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W + tk.E + tk.N, padx=10, pady=2)
        # 串口列表下拉菜单
        self.state = tk.StringVar()
        state_label = ttk.Label(status_frame, font=('微软雅黑', 10), textvariable=self.state, foreground='black', )
        state_label.grid(row=0, column=0, sticky=tk.W)
        # close_button = ttk.Button(status_frame, text="安全退出", command=self.close_program)
        # close_button.grid(row=0, column=0, sticky=tk.W, padx=800)

    def close_program(self):
        self.close_serial_port()
        time.sleep(0.02)
        sys.exit()
        # self.destroy()


# 启动程序
if __name__ == "__main__":
    app = SerialAssistant()
    app.start_receive_save_plot_data()
    app.mainloop()
