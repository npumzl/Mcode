import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建布局和窗口
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # 创建绘图窗口
        self.plot = pg.PlotWidget(title='动态更新曲线')
        layout.addWidget(self.plot)

        # 创建启动和停止按钮
        self.start_button = QPushButton('启动')
        self.stop_button = QPushButton('停止')
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # 绑定按钮点击事件
        self.start_button.clicked.connect(self.start_plot)
        self.stop_button.clicked.connect(self.stop_plot)

        # 初始化数据和定时器
        self.a = np.random.random(100)
        self.b = np.random.random(50)
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)

    # 更新数据函数
    def update_data(self):
        self.a = np.random.random(100)
        self.b = np.random.random(50)
        self.plot.plot(self.a, pen='g', clear=True)  # 清空并绘制a的曲线
        self.plot.plot(self.b, pen='r')  # 绘制b的曲线

    # 启动绘图
    def start_plot(self):
        self.timer.start(50)  # 每隔100ms更新一次数据

    # 停止绘图
    def stop_plot(self):
        self.timer.stop()


# 创建QApplication实例和MainWindow窗口
app = QApplication([])
window = MainWindow()
window.show()

# 启动事件循环
app.exec_()
