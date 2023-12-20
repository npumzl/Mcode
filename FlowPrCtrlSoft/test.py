from PyQt5.Qt import *
import sys
import math

App = QApplication(sys.argv)
Win = QWidget()
Win.setWindowTitle("QLineEdit-功能测试")
Win.setWindowIcon(QIcon("D:\ICO\ooopic_1517621175.ico"))
Win.resize(500, 500)

le2 = QLineEdit(Win)
le2.resize(50, 50)
le2.move(20, 20)

le = QLineEdit(Win)
le.resize(300, 300)
le.move(100, 100)

le.textEdited.connect(lambda val: print("文本框编辑的时候", val))  # 文本框编辑事件
le.textChanged.connect(lambda val: print("文本框内容发生改变", val))  # 文本框改变事件
le.returnPressed.connect(lambda: print("回车键被按下"))
le.returnPressed.connect(lambda: le2.setFocus())
le.editingFinished.connect(lambda: print("结束编辑"))
le.cursorPositionChanged.connect(lambda old_Pos, new_Pos: print(old_Pos, new_Pos))  # 焦点发生改变
le.selectionChanged.connect(lambda: print("选中文本发生改变", le.selectedText()))  # 选中文本发生改变事件

Win.show()
sys.exit(App.exec_())