# 导入tkinter库，并从math库中导入gcd函数
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
import sv_ttk


# style_default = ttk.Style()
# style_default.configure("Label", font=('Consolas', 14), width=8, height=2)
# style_default.configure("Label2", font=('Consolas', 14),width=20, height=25)
# style_default.configure("entry",  font=('Consolas', 12), width=10)


# 定义一个函数，与按钮链接
def clicked():
    try:
        x = int(entry1.get())
        y = int(entry2.get())
        Result_List = []
        right = y
        for i in range(100):
            temp = right / x
            temptemp = round(temp, 2)
            temptemp = "第{}次：".format(str(i + 1)) + str(temptemp)
            Result_List.append(temptemp)
            right = right + temp
        str1 = "\n".join(Result_List[0:25])
        str2 = "\n".join(Result_List[25:50])
        str3 = "\n".join(Result_List[50:75])
        str4 = "\n".join(Result_List[75:100])
        result1.set(str1)
        result2.set(str2)
        result3.set(str3)
        result4.set(str4)
    except:
        messagebox.showwarning('warning', '发生计算错误,请检查输入数据是否正确！')


# 创建窗口
window = tk.Tk()
window.title('博弈计算软件')
window.geometry('600x490')

# 创建标签
label1 = ttk.Label(window, text='中奖倍率')
label2 = ttk.Label(window, text='期望中奖金额')
label1.place(x=10, y=10)
label2.place(x=10, y=60)

# 创建输入框，设定宽度为10
entry1 = ttk.Entry(window)
entry1.insert(0, '20')
entry2 = ttk.Entry(window)
entry2.insert(0, '20')
entry1.place(x=10, y=30, width=100)
entry2.place(x=10, y=80, width=100)

# 创建按钮，使用command属性链接函数clicked（不能带参数）
button = ttk.Button(window, text='开始求解', command=clicked)
button.place(x=15, y=120)

result_group = ttk.LabelFrame(window, text="计算结果")
result_group.place(x=140, y=10, width=440, height=460)

step = ttk.LabelFrame(window, text="使用方法")
step.place(x=10, y=170, width=120, height=200)

label3 = ttk.Label(step, text='1.输入中奖倍率\n'
                              '2.输入预期中奖金额\n'
                              '3.点击开始计算')
label3.pack()

# 创建文本框并放置
result1 = tk.StringVar()
result2 = tk.StringVar()
result3 = tk.StringVar()
result4 = tk.StringVar()
text1 = ttk.Label(result_group, textvariable=result1)
text2 = ttk.Label(result_group, textvariable=result2)
text3 = ttk.Label(result_group, textvariable=result3)
text4 = ttk.Label(result_group, textvariable=result4)
text1.grid(row=0, column=1, padx=5, pady=5)
text2.grid(row=0, column=2, padx=5, pady=5)
text3.grid(row=0, column=3, padx=5, pady=5)
text4.grid(row=0, column=4, padx=5, pady=5)
# sv_ttk.set_theme("light")
# 窗口循环
window.mainloop()
