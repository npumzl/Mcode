import tkinter as tk
from tkinter import messagebox
from loguru import logger
import os
import math
import sys


# 显示使用日志
def show_log():
    cmd = 'start' + r'.\使用日志.log'
    os.system(cmd)


# 定义一个类
class Calculate():
    def __init__(self):
        # 进行初始化

        self.window = tk.Tk()
        self.window.title("CCM模式下Boost和Buck电路参数计算器")
        self.window.resizable(0, 0)
        sw = self.window.winfo_screenwidth()
        # 得到屏幕宽度
        sh = self.window.winfo_screenheight()

        # 得到屏幕高度
        ww = 580
        wh = 325
        # 根据使用者屏幕合理调整界面大小
        x = (sw - ww) / 2
        y = (sh - wh) / 2
        self.window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
        self.window.attributes('-alpha', 1)
        #     创建菜单栏
        self.menubar = tk.Menu(self.window)
        self.window.config(menu=self.menubar)
        #    创建下拉菜单
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        # self.filemenu.add_command(label='新建')
        self.filemenu.add_command(label='保存数据', command=self.save_data)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="退出", command=self.quit)
        self.menubar.add_cascade(label='文件', menu=self.filemenu)
        self.menubar.add_command(label='使用帮助', command=self.help)
        self.menubar.add_command(label='初始化', command=self.init_data)
        self.menubar.add_command(label='关于', command=self.about)

        # 分区域
        self.Boost_area = tk.Label(self.window, text='Boost', font=('微软雅黑', 25))
        self.Buck_area = tk.Label(self.window, text='Buck', font=('微软雅黑', 25))
        #     Boost参数区域
        self.Boost_Uimin_label = tk.Label(self.window, text='Uimin', font=('微软雅黑', 10))
        self.Boost_Uimax_label = tk.Label(self.window, text='Uimax', font=('微软雅黑', 10))
        self.Boost_Iomin_label = tk.Label(self.window, text='Iomin', font=('微软雅黑', 10))
        self.Boost_Iomax_label = tk.Label(self.window, text='Iomax', font=('微软雅黑', 10))
        self.Boost_Uo_label = tk.Label(self.window, text='Uo', font=('微软雅黑', 10))
        self.Boost_fs_label = tk.Label(self.window, text='fs', font=('微软雅黑', 10))
        self.Boost_ripple_label = tk.Label(self.window, text='delta_U', font=('微软雅黑', 10))

        self.Boost_Uimin = tk.StringVar()
        self.Boost_Uimax = tk.StringVar()
        self.Boost_Iomin = tk.StringVar()
        self.Boost_Iomax = tk.StringVar()
        self.Boost_Uo = tk.StringVar()
        self.Boost_fs = tk.StringVar()
        self.Boost_ripple = tk.StringVar()
        self.entry_Boost_Uimin = tk.Entry(self.window, textvariable=self.Boost_Uimin, width=10, justify='right')
        self.entry_Boost_Uimax = tk.Entry(self.window, textvariable=self.Boost_Uimax, width=10, justify='right')
        self.entry_Boost_Iomin = tk.Entry(self.window, textvariable=self.Boost_Iomin, width=10, justify='right')
        self.entry_Boost_Iomax = tk.Entry(self.window, textvariable=self.Boost_Iomax, width=10, justify='right')
        self.entry_Boost_Uo = tk.Entry(self.window, textvariable=self.Boost_Uo, width=10, justify='right')
        self.entry_Boost_fs = tk.Entry(self.window, textvariable=self.Boost_fs, width=10, justify='right')
        self.entry_Boost_ripple = tk.Entry(self.window, textvariable=self.Boost_ripple, width=10, justify='right')

        # Buck参数区域
        #     Boost参数区域
        self.Buck_Uimin_label = tk.Label(self.window, text='Uimin', font=('微软雅黑', 10))
        self.Buck_Uimax_label = tk.Label(self.window, text='Uimax', font=('微软雅黑', 10))
        self.Buck_Iomin_label = tk.Label(self.window, text='Iomin', font=('微软雅黑', 10))
        self.Buck_Iomax_label = tk.Label(self.window, text='Iomax', font=('微软雅黑', 10))
        self.Buck_Uo_label = tk.Label(self.window, text='Uo', font=('微软雅黑', 10))
        self.Buck_fs_label = tk.Label(self.window, text='fs', font=('微软雅黑', 10))
        self.Buck_ripple_label = tk.Label(self.window, text='ripple', font=('微软雅黑', 10))

        self.Buck_Uimin = tk.StringVar()
        self.Buck_Uimax = tk.StringVar()
        self.Buck_Iomin = tk.StringVar()
        self.Buck_Iomax = tk.StringVar()
        self.Buck_Uo = tk.StringVar()
        self.Buck_fs = tk.StringVar()
        self.Buck_ripple = tk.StringVar()

        self.Buck_Uimin.set('10')
        self.Buck_Uimax.set('15')
        self.Buck_Iomin.set('0.1')
        self.Buck_Iomax.set('1')
        self.Buck_Uo.set('5')
        self.Buck_fs.set('40')
        self.Buck_ripple.set('1')

        self.Boost_Uimin.set('10')
        self.Boost_Uimax.set('15')
        self.Boost_Iomin.set('0.5')
        self.Boost_Iomax.set('0.7')
        self.Boost_Uo.set('24')
        self.Boost_fs.set('55')
        self.Boost_ripple.set('0.5')

        self.entry_Buck_Uimin = tk.Entry(self.window, textvariable=self.Buck_Uimin, width=10, justify='right', )
        self.entry_Buck_Uimax = tk.Entry(self.window, textvariable=self.Buck_Uimax, width=10, justify='right')
        self.entry_Buck_Iomin = tk.Entry(self.window, textvariable=self.Buck_Iomin, width=10, justify='right')
        self.entry_Buck_Iomax = tk.Entry(self.window, textvariable=self.Buck_Iomax, width=10, justify='right')
        self.entry_Buck_Uo = tk.Entry(self.window, textvariable=self.Buck_Uo, width=10, justify='right')
        self.entry_Buck_fs = tk.Entry(self.window, textvariable=self.Buck_fs, width=10, justify='right')
        self.entry_Buck_ripple = tk.Entry(self.window, textvariable=self.Buck_ripple, width=10, justify='right')

        #     Button
        self.button1 = tk.Button(self.window, text="清空数据", command=self.Boost_clear, relief='groove')
        self.button2 = tk.Button(self.window, text="计算参数", command=self.Boost_calcute, relief='groove')
        self.button3 = tk.Button(self.window, text="清空数据", command=self.Buck_clear, relief='groove')
        self.button4 = tk.Button(self.window, text="计算参数", command=self.Buck_calcute, relief='groove')

        self.boost_res = ''
        self.buck_res = ''

    def arrange(self):
        self.Boost_area.place(x=80, y=10)
        self.Buck_area.place(x=400, y=10)
        #     boost
        self.Boost_Uimin_label.place(x=55, y=100)
        self.Boost_Uimax_label.place(x=55, y=125)
        self.Boost_Iomin_label.place(x=55, y=150)
        self.Boost_Iomax_label.place(x=55, y=175)
        self.Boost_Uo_label.place(x=55, y=200)
        self.Boost_fs_label.place(x=55, y=225)
        self.Boost_ripple_label.place(x=55, y=250)

        self.entry_Boost_Uimin.place(x=105, y=100)
        self.entry_Boost_Uimax.place(x=105, y=125)
        self.entry_Boost_Iomin.place(x=105, y=150)
        self.entry_Boost_Iomax.place(x=105, y=175)
        self.entry_Boost_Uo.place(x=105, y=200)
        self.entry_Boost_fs.place(x=105, y=225)
        self.entry_Boost_ripple.place(x=105, y=250)

        tk.Label(self.window, text='(V)').place(x=180, y=100)
        tk.Label(self.window, text='(V)').place(x=180, y=125)
        tk.Label(self.window, text='(A)').place(x=180, y=150)
        tk.Label(self.window, text='(A)').place(x=180, y=175)
        tk.Label(self.window, text='(V)').place(x=180, y=200)
        tk.Label(self.window, text='(KHz)').place(x=180, y=225)
        tk.Label(self.window, text='(V)').place(x=180, y=250)

        self.Buck_Uimin_label.place(x=360, y=100)
        self.Buck_Uimax_label.place(x=360, y=125)
        self.Buck_Iomin_label.place(x=360, y=150)
        self.Buck_Iomax_label.place(x=360, y=175)
        self.Buck_Uo_label.place(x=360, y=200)
        self.Buck_fs_label.place(x=360, y=225)
        self.Buck_ripple_label.place(x=360, y=250)

        self.entry_Buck_Uimin.place(x=415, y=100)
        self.entry_Buck_Uimax.place(x=415, y=125)
        self.entry_Buck_Iomin.place(x=415, y=150)
        self.entry_Buck_Iomax.place(x=415, y=175)
        self.entry_Buck_Uo.place(x=415, y=200)
        self.entry_Buck_fs.place(x=415, y=225)
        self.entry_Buck_ripple.place(x=415, y=250)

        tk.Label(self.window, text='(V)').place(x=490, y=100)
        tk.Label(self.window, text='(V)').place(x=490, y=125)
        tk.Label(self.window, text='(A)').place(x=490, y=150)
        tk.Label(self.window, text='(A)').place(x=490, y=175)
        tk.Label(self.window, text='(V)').place(x=490, y=200)
        tk.Label(self.window, text='(KHz)').place(x=490, y=225)
        tk.Label(self.window, text='(%)').place(x=490, y=250)

        self.button1.place(x=80, y=280)
        self.button2.place(x=150, y=280)
        self.button3.place(x=390, y=280)
        self.button4.place(x=460, y=280)

    # 打开使用日志
    def open_log(self):
        os.system('chcp 65001')
        try:
            cmd = 'start' + r'.\使用日志.log'
            os.system(cmd)
        except:
            messagebox.showwarning('Warning', '打开失败，请检查是否占用！')

    # 清理BOOST参数
    def Boost_clear(self):
        self.Boost_Uimin.set('')
        self.Boost_Uimax.set('')
        self.Boost_Iomin.set('')
        self.Boost_Iomax.set('')
        self.Boost_Uo.set('')
        self.Boost_fs.set('')
        self.Boost_ripple.set('')

    # 计算BOOST参数
    def Boost_calcute(self):
        try:
            dataa_D = ''
            dataa_L = ''
            dataa_C = ''
            dataa_fc = ''
            dataa_ripple = ''
            str_1 = ''
            str_2 = ''
            Uimin = float(self.Boost_Uimin.get())
            Uimax = float(self.Boost_Uimax.get())
            Iomin = float(self.Boost_Iomin.get())
            Iomax = float(self.Boost_Iomax.get())
            Uo = float(self.Boost_Uo.get())
            fs = float(self.Boost_fs.get()) * 1000
            delta_U = float(self.Boost_ripple.get())
            c = tk.StringVar()
            # 求占空比D范围
            Dmin = 1 - Uimax / Uo
            Dmax = 1 - Uimin / Uo

            if Dmax < (1 / 3):
                D = Dmax
            elif Dmin < (1 / 3) and Dmax > (1 / 3):
                D = 1 / 3
            else:
                D = Dmin
            # 求电感L的临界值
            Lmin = Uo * D * ((1 - D) ** 2) / (2 * Iomin * fs)

            # RC电路的截止频率fc
            fc = delta_U * fs / (Uo * Dmax)

            # 电容C的临界值
            Rmin = Uo / Iomax
            Cmin = 1 / (Rmin * fc)
            # 输出计算数据
            print("占空比D:{:.3f} - {:.3f}".format(Dmin, Dmax))
            dataa_D = "占空比D:{:.3f} - {:.3f}".format(Dmin, Dmax)
            self.boost_res = "占空比D:{:.3f} - {:.3f}".format(Dmin, Dmax) + '\n'
            if int(Lmin) == 0:
                Lmin *= 1000
                if int(Lmin) == 0:
                    Lmin *= 1000
                    print("电感L的值应大于{:.1f}uH".format(Lmin))
                    self.boost_res += "电感L的值应大于{:.1f}uH".format(Lmin) + '\n'
                    dataa_L = "电感L的值应大于{:.1f}uH".format(Lmin)
                else:
                    print("电感L的值应大于{:.1f}mH".format(Lmin))
                    self.boost_res += "电感L的值应大于{:.1f}mH".format(Lmin) + '\n'
                    dataa_L = "电感L的值应大于{:.1f}mH".format(Lmin)
            else:
                print("电感L的值应大于{:.1f}H".format(Lmin))
                self.boost_res += "电感L的值应大于{:.1f}H".format(Lmin) + '\n'
                dataa_L = "电感L的值应大于{:.1f}H".format(Lmin)
            if (fc / (10 ** 6)) > 1:
                print("RC电路的最大截止频率:{:.1f}MHz".format(fc / (10 ** 6)))
                self.boost_res += "RC电路的最大截止频率:{:.1f}MHz".format(fc / (10 ** 6)) + '\n'
                dataa_fc = "RC电路的最大截止频率:{:.1f}MHz".format(fc / (10 ** 6))
            elif (fc / (10 ** 3)) > 1:
                print("RC电路的最大截止频率:{:.1f}kHz".format(fc / (10 ** 3)))
                self.boost_res += "RC电路的最大截止频率:{:.1f}kHz".format(fc / (10 ** 3)) + '\n'
                dataa_fc = "RC电路的最大截止频率:{:.1f}kHz".format(fc / (10 ** 3))
            else:
                print("RC电路的最大截止频率:{:.1f}Hz".format(fc))
                self.boost_res += "RC电路的最大截止频率:{:.1f}Hz".format(fc) + '\n'
                dataa_fc = "RC电路的最大截止频率:{:.1f}Hz".format(fc)
            if int(Cmin) == 0:
                Cmin *= 1000
                if int(Cmin) == 0:
                    Cmin *= 1000
                    print("电容C的值应大于{:.1f}uF".format(Cmin))
                    self.boost_res += "电容C的值应大于{:.1f}uF".format(Cmin) + '\n'
                    dataa_C = "电容C的值应大于{:.1f}uF".format(Cmin)
                    c.set(int(Cmin + 100))
                else:
                    print("电容C的值应大于{:.1f}mF".format(Cmin))
                    self.boost_res += "电容C的值应大于{:.1f}mF".format(Cmin) + '\n'
                    dataa_C = "电容C的值应大于{:.1f}mF".format(Cmin)
                    c.set(Cmin * 1000)
            else:
                print("电容C的值应大于{:.1f}F".format(Cmin))
                self.boost_res += "电容C的值应大于{:.1f}F".format(Cmin) + '\n'
                dataa_C = "电容C的值应大于{:.1f}F".format(Cmin)
                c.set(Cmin * 1000000)
            # messagebox.showinfo('Boost参数计算结果', self.buck_res)

            window_child = tk.Toplevel(self.window)
            sw = self.window.winfo_screenwidth()
            # 得到屏幕宽度
            sh = self.window.winfo_screenheight()

            # 得到屏幕高度
            ww = 280
            wh = 300

            x = (sw - ww) / 2
            y = (sh - wh) / 2
            window_child.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
            window_child.title('请填写实际参数')

            tk.Label(window_child, text=dataa_D, font=('微软雅黑', 10), fg='red').place(x=10, y=10)
            tk.Label(window_child, text=dataa_L, font=('微软雅黑', 10), fg='red').place(x=10, y=30)
            tk.Label(window_child, text=dataa_fc, font=('微软雅黑', 10), fg='red').place(x=10, y=50)
            tk.Label(window_child, text=dataa_C, font=('微软雅黑', 10), fg='red').place(x=10, y=70)
            tk.Label(window_child, text='请输入实际的电容值C(uH)', font=('微软雅黑', 10)).place(x=10, y=90)
            entry_C = tk.Entry(window_child, textvariable=c, width=5, justify='left')
            entry_C.place(x=180, y=93)
            C_actual = 0

            def click_3():
                global str_2, str_1
                C_actual = c.get()
                C_actual = float(C_actual)
                self.boost_res += '实际的选取电容值C为{}uF'.format(C_actual) + '\n'
                C_actual /= (10 ** 6)

                # RC电路的实际截止频率fc_actual
                fc_actual = 1 / Rmin / C_actual

                # 实际纹波值
                delta_U_actual = Dmax * Uo / (Rmin * C_actual * fs)

                # 输出数据
                if fc_actual < fc and delta_U_actual < delta_U:
                    print("参加计算正常")
                    if (fc_actual / (10 ** 6)) > 1:
                        print("RC电路的实际截止频率:{:.1f}MHz".format(fc_actual / (10 ** 6)))
                        str_1 = "RC电路的实际截止频率:{:.1f}MHz".format(fc_actual / (10 ** 6))
                        self.boost_res += str_1 + '\n'

                    elif (fc_actual / (10 ** 3)) > 1:
                        print("RC电路的实际截止频率:{:.1f}kHz".format(fc_actual / (10 ** 3)))
                        str_1 = "RC电路的实际截止频率:{:.1f}kHz".format(fc_actual / (10 ** 3))
                        self.boost_res += str_1 + '\n'
                    else:
                        print("RC电路的实际截止频率:{:.1f}Hz".format(fc_actual))
                        str_1 = "RC电路的实际截止频率:{:.1f}Hz".format(fc_actual)
                        self.boost_res += str_1 + '\n'

                    print("实际纹波电压为{:.2f}V".format(delta_U_actual))
                    str_2 = "实际纹波电压为{:.2f}V".format(delta_U_actual)
                    self.boost_res += str_2 + '\n'
                else:
                    print("参数计算有误")
                    messagebox.showwarning('warning', '发生计算错误！')
                tk.Label(window_child, text=str_1, font=('微软雅黑', 10), fg='red').place(x=10, y=150)
                tk.Label(window_child, text=str_2, font=('微软雅黑', 10), fg='red').place(x=10, y=170)

                def click_4():
                    window_child.destroy()
                    print('\n' + '*' * 5 + '最终结果' + '*' * 5 + '\n' + self.boost_res)

                tk.Button(window_child, text="关闭", command=click_4, relief='groove').place(x=75, y=200)

            tk.Button(window_child, text="下一步", command=click_3, relief='groove').place(x=70, y=120)
        except:
            messagebox.showwarning('ERROR', '发生错误，请检查！')

    # 清理BUCK参数
    def Buck_clear(self):
        self.Buck_Uimin.set('')
        self.Buck_Uimax.set('')
        self.Buck_Iomin.set('')
        self.Buck_Iomax.set('')
        self.Buck_Uo.set('')
        self.Buck_fs.set('')
        self.Buck_ripple.set('')

    # 计算BUCK参数
    def Buck_calcute(self, ):
        try:

            Uimin = float(self.Buck_Uimin.get())
            Uimax = float(self.Buck_Uimax.get())
            Iomin = float(self.Buck_Iomin.get())
            Iomax = float(self.Buck_Iomax.get())
            Uo = float(self.Buck_Uo.get())
            fs = float(self.Buck_fs.get()) * 1000
            delta = float(self.Buck_ripple.get()) / 100

            # 求占空比D范围
            Dmin = Uo / Uimax
            Dmax = Uo / Uimin

            # 求电感L的临界值
            Lmin = Uo * (1 - Dmin) / (2 * Iomin * fs)

            self.buck_res = '发生计算错误，请检查数据是否正确！'
            # 输出计算数据
            print("占空比D:{:.3f} - {:.3f}".format(Dmin, Dmax))
            self.buck_res = "占空比D:{:.3f} - {:.3f}".format(Dmin, Dmax) + '\n'
            data_D = "占空比D:{:.3f} - {:.3f}".format(Dmin, Dmax)
            l = tk.StringVar()
            data_L = ''
            if int(Lmin) == 0:
                Lmin *= 1000
                if int(Lmin) == 0:
                    Lmin *= 1000
                    print("电感L的值应大于{:.1f}uH".format(Lmin))
                    l.set(int(Lmin + 1))
                    self.buck_res += "电感L的值应大于{:.1f}uH".format(Lmin) + '\n'
                    data_L = ("电感L的值应大于{:.1f}uH".format(Lmin))
                else:
                    print("电感L的值应大于{:.1f}mH".format(Lmin))
                    l.set(Lmin * 1000)
                    self.buck_res += "  电感L的值应大于{:.1f}mH".format(Lmin) + '\n'
                    data_L = ("电感L的值应大于{:.1f}mH".format(Lmin))
            else:
                print("电感L的值应大于{:.1f}H".format(Lmin))
                l.set(Lmin * 1000000)
                self.buck_res += "  电感L的值应大于{:.1f}H".format(Lmin) + '\n'
                data_L = ("电感L的值应大于{:.1f}H".format(Lmin))
            # 输入实际的电感值
            l.set(int((float(l.get()))))
            window_child = tk.Toplevel(self.window)
            sw = self.window.winfo_screenwidth()
            # 得到屏幕宽度
            sh = self.window.winfo_screenheight()

            # 得到屏幕高度
            ww = 280
            wh = 300

            x = (sw - ww) / 2
            y = (sh - wh) / 2
            window_child.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
            window_child.title('请填写实际参数')

            tk.Label(window_child, text=data_D, font=('微软雅黑', 10), fg='red').place(x=10, y=10)
            tk.Label(window_child, text=data_L, font=('微软雅黑', 10), fg='red').place(x=10, y=30)
            tk.Label(window_child, text='请输入实际的电感值L(uH)', font=('微软雅黑', 10)).place(x=10, y=50)
            entry_L = tk.Entry(window_child, textvariable=l, width=5, justify='left')
            entry_L.place(x=180, y=53)
            L_actual = 0

            def click_1():
                L_actual = float(l.get())
                print(L_actual)
                L_actual /= (10 ** 6)
                print(L_actual)
                c = tk.StringVar()

                # RC电路的截止频率fc
                fc = fs / math.pi * math.sqrt(2 * delta / (1 - Dmin))
                data_C = ''
                data_fc = ''
                data_ripple = ''
                # 电容C的临界值
                Cmin = 1 / (4 * (math.pi ** 2) * L_actual * (fc ** 2))
                if (fc / (10 ** 6)) > 1:
                    print("RC电路的最大截止频率:{:.1f}MHz".format(fc / (10 ** 6)))
                    self.buck_res += "RC电路的最大截止频率:{:.1f}MHz".format(fc / (10 ** 6)) + '\n'
                    data_fs = "RC电路的最大截止频率:{:.1f}MHz".format(fc / (10 ** 6))
                elif (fc / (10 ** 3)) > 1:
                    print("RC电路的最大截止频率:{:.1f}kHz".format(fc / (10 ** 3)))
                    self.buck_res += "RC电路的最大截止频率:{:.1f}kHz".format(fc / (10 ** 3)) + '\n'
                    data_fs = "RC电路的最大截止频率:{:.1f}kHz".format(fc / (10 ** 3))
                else:
                    print("RC电路的最大截止频率:{:.1f}Hz".format(fc))
                    self.buck_res += "RC电路的最大截止频率:{:.1f}Hz".format(fc) + '\n'
                    data_fs = "RC电路的最大截止频率:{:.1f}Hz".format(fc)
                if int(Cmin) == 0:
                    Cmin *= 1000
                    if int(Cmin) == 0:
                        Cmin *= 1000
                        print("电容C的值应大于{:.1f}uF".format(Cmin))
                        self.buck_res += "电容C的值应大于{:.1f}uF".format(Cmin) + '\n'
                        data_C = "电容C的值应大于{:.1f}uF".format(Cmin)
                        c.set(int(Cmin * 5))
                    else:
                        print("电容C的值应大于{:.1f}mF".format(Cmin))
                        self.buck_res += "电容C的值应大于{:.1f}mF".format(Cmin) + '\n'
                        data_C = "电容C的值应大于{:.1f}mF".format(Cmin)
                        c.set(Cmin * 1000)
                else:
                    print("电容C的值应大于{:.1f}F".format(Cmin))
                    self.buck_res += "电容C的值应大于{:.1f}F".format(Cmin) + '\n'
                    data_C = "电容C的值应大于{:.1f}F".format(Cmin)
                    c.set(Cmin * 1000000)
                tk.Label(window_child, text=data_fs, font=('微软雅黑', 10), fg='red').place(x=10, y=110)
                tk.Label(window_child, text=data_C, font=('微软雅黑', 10), fg='red').place(x=10, y=130)
                tk.Label(window_child, text='请输入实际的电容值C(uF)', font=('微软雅黑', 10)).place(x=10, y=150)
                c.set((float(c.get()) + 1))
                entry_C = tk.Entry(window_child, textvariable=c, width=5, justify='left')
                entry_C.place(x=180, y=150)
                C_actual = 0

                def click_2():
                    C_actual = c.get()
                    self.buck_res += '实际选取的电容值为{}uF'.format(C_actual) + '\n'
                    C_actual = float(C_actual) / (10 ** 6)

                    # RC电路的实际截止频率fc_actual
                    fc_actual = 1 / (2 * math.pi * math.sqrt(C_actual * L_actual))

                    # 实际纹波值delta_actual
                    delta_actual = (math.pi ** 2) / 2 * ((fc_actual / fs) ** 2) * (1 - Dmin)

                    # 输出数据
                    if (fc_actual < fc) and (delta_actual < delta):
                        print("参数计算正常")
                        if (fc_actual / (10 ** 6)) > 1:
                            print("RC电路的实际截止频率:{:.1f}MHz".format(fc_actual / (10 ** 6)))
                            data_fc = "RC电路的实际截止频率:{:.1f}MHz".format(fc_actual / (10 ** 6))
                            self.buck_res += (data_fc + '\n')
                        elif (fc_actual / (10 ** 3)) > 1:
                            print("RC电路的实际截止频率:{:.1f}kHz".format(fc_actual / (10 ** 3)))
                            data_fc = "RC电路的实际截止频率:{:.1f}kHz".format(fc_actual / (10 ** 3))
                            self.buck_res += (data_fc + '\n')
                        else:
                            print("RC电路的实际截止频率:{:.1f}Hz".format(fc_actual))
                            data_fc = "RC电路的实际截止频率:{:.1f}Hz".format(fc_actual)
                            self.buck_res += (data_fc + '\n')
                        print("实际纹波比为{:.2f}%".format(delta_actual * 100))
                        self.buck_res += ("实际纹波比为{:.2f}%".format(delta_actual * 100) + '\n')
                        data_ripple = "实际纹波比为{:.2f}%".format(delta_actual * 100)
                        tk.Label(window_child, text=data_fc, font=('微软雅黑', 10), fg='red').place(x=10, y=210)
                        tk.Label(window_child, text=data_ripple, font=('微软雅黑', 10), fg='red').place(x=10, y=230)

                    else:
                        print("参数计算有误")
                        messagebox.showwarning('错误', '"参数计算错误！"')
                    close.place(x=75, y=260)

                def clo():
                    window_child.destroy()
                    print('\n' + '*' * 5 + '最终结果' + '*' * 5 + '\n' + self.buck_res)

                tk.Button(window_child, text="下一步", command=click_2, relief='groove').place(x=70, y=180)
                close = tk.Button(window_child, text="关闭", command=clo, relief='groove')

            tk.Button(window_child, text="下一步", command=click_1, relief='groove').place(x=70, y=80)
        # 若发生错误，提示使用者
        except:
            messagebox.showwarning('ERROR', '发生错误，请检查！')

    # 退出程序
    def quit(self):
        self.window.quit()
        self.window.destroy()
        exit()

    # 保存计算数据
    def save_data(self):
        logger.add("使用日志.log", rotation="500MB", encoding="utf-8", enqueue=True, compression="zip",
                   retention="10 days")
        if self.boost_res != '':
            result = 'Boost_Uimin =  ' + self.Boost_Uimin.get() + '\n' + 'Boost_Uimax =  ' + self.Boost_Uimax.get() + '\n' + 'Boost_Iomin =  ' + self.Boost_Iomin.get() + '\n' + 'Boost_Iomax =  ' + self.Boost_Iomax.get() + '\n' + 'Boost_Uo = ' + self.Boost_Uo.get() + '\n' + 'Boost_fs = ' + self.Boost_fs.get() + '\n' + 'Boost_ripple = ' + self.Boost_ripple.get() + '\n'
            logger.info('\n' + result + self.boost_res)
            messagebox.showinfo('提示', 'boost参数保存成功！')
        if self.buck_res != '':
            result = 'Buck_Uimin =  ' + self.Buck_Uimin.get() + '\n' + 'Buck_Uimax =  ' + self.Buck_Uimax.get() + '\n' + 'Buck_Iomin =  ' + self.Buck_Iomin.get() + '\n' + 'Buck_Iomax =  ' + self.Buck_Iomax.get() + '\n' + 'Buck_Uo = ' + self.Buck_Uo.get() + '\n' + 'Buck_fs = ' + self.Buck_fs.get() + '\n' + 'Buck_ripple = ' + self.Buck_ripple.get() + '\n'
            logger.info('\n' + result + self.buck_res)
            messagebox.showinfo('提示', 'buck参数保存成功！')
        if (self.boost_res == '') and (self.buck_res == ''):
            messagebox.showinfo('提示', '未检测到使用痕迹！')

    # 显示使用帮助
    def help(self):
        messagebox.showinfo('欢迎使用', '   此工具用于计算Boost和Buck电路的一系列参数，请按提示使用即可。\nBoost和Buck参数计算为两个完全独立的模块，在对应数据栏中输入'
                                    '参数点击“进行计算”便可实现功能\n   本软件已在数据栏中填入了示例数据，感谢使用！')

    # 显示关于
    def about(self):
        string = '  本软件为本人学习实践之余制作的一款Boost和Buck电路参数计算软件，方便进行研究学习，感谢使用！'
        messagebox.showinfo('关于', string)

    # 初始化数据
    def init_data(self):
        self.buck_res = ''
        self.boost_res = ''
        self.Buck_Uimin.set('10')
        self.Buck_Uimax.set('15')
        self.Buck_Iomin.set('0.1')
        self.Buck_Iomax.set('1')
        self.Buck_Uo.set('5')
        self.Buck_fs.set('40')
        self.Buck_ripple.set('1')

        self.Boost_Uimin.set('10')
        self.Boost_Uimax.set('15')
        self.Boost_Iomin.set('0.5')
        self.Boost_Iomax.set('0.7')
        self.Boost_Uo.set('24')
        self.Boost_fs.set('55')
        self.Boost_ripple.set('0.5')
        messagebox.showinfo('成功', '数据初始化成功！')


def main():
    start = Calculate()
    start.arrange()
    tk.mainloop()


if __name__ == '__main__':
    main()
