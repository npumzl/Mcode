# 导入tkinter库，并从math库中导入gcd函数
import tkinter as tk
import tkinter.messagebox as messagebox
# import sv_ttk


# 定义一个函数，与按钮链接
def clicked():
    try:
        # 清空text框
        text1.delete(1.0, 'end')
        text2.delete(1.0, 'end')
        text3.delete(1.0, 'end')
        text4.delete(1.0, 'end')

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
        # mes = tk.Message(window, text=str1, font=('Consolas', 14), width=12)
        # label2 = tk.Label(window, text=str1, font=('Consolas', 14), width=12, height=100)

        text1.insert('insert', str1)
        text2.insert('insert', str2)
        text3.insert('insert', str3)
        text4.insert('insert', str4)
    except:
        messagebox.showwarning('warning', '发生计算错误,请检查输入数据是否正确！')


# 创建窗口
window = tk.Tk()
window.title('博弈计算软件')
window.geometry('950x600')

# 创建标签
label1 = tk.Label(window, text='中奖倍率', font=('Consolas', 14), width=8, height=2)
label2 = tk.Label(window, text='期望中奖金额', font=('Consolas', 14), width=12, height=2)
# 使用grid放置标签，将标签分别放在第0行第0列和第0行第1列
label1.grid(row=0, column=0)
label2.grid(row=0, column=1)

# 创建输入框，设定宽度为10
entry1 = tk.Entry(window, font=('Consolas', 12), width=10)
entry2 = tk.Entry(window, font=('Consolas', 12), width=10)
# 使用grid放置输入框，将它们分别放在第1行第0列和第1行第1列，并调整水平间距为5
entry1.grid(row=1, column=0, padx=5)
entry2.grid(row=1, column=1, padx=5)

# 创建按钮，使用command属性链接函数clicked（不能带参数）
button = tk.Button(window, text='开始求解', font=('Consolas', 14),
                   width=12, height=2, command=clicked)
# 放置按钮，调整水平间距为5，垂直间距为20
button.grid(row=2, column=0, padx=5, pady=20)

# 创建文本框并放置
text1 = tk.Text(window, font=('Consolas', 12), width=20, height=25)
text2 = tk.Text(window, font=('Consolas', 12), width=20, height=25)
text3 = tk.Text(window, font=('Consolas', 12), width=20, height=25)
text4 = tk.Text(window, font=('Consolas', 12), width=20, height=25)
text1.grid(row=2, column=1, padx=5, pady=20)
text2.grid(row=2, column=2, padx=5, pady=20)
text3.grid(row=2, column=3, padx=5, pady=20)
text4.grid(row=2, column=4, padx=5, pady=20)
# sv_ttk.set_theme("white")
# 窗口循环
window.mainloop()
