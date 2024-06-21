# code:utf-8
# Create by Maxtang
# 2023/5/3
import psutil
import sys
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import QTimer, QThread, pyqtSignal 
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

# 折线图怎么画
# ref： https://zhuanlan.zhihu.com/p/380870186
# 另外开一个线程来跑，避免和主线程的定时器冲突造成阻塞
# ref: https://geek-docs.com/pyqt5/pyqt5-questions/60_pyqt5_pyqt5_qthread_signal_not_working_gui_freeze.html
# 折线图随时间变化
# ref: https://blog.csdn.net/A13784130845/article/details/126630182
class MyWorker(QThread):
    timeout = pyqtSignal()

    def __init__(self):
        super(MyWorker, self).__init__()

    def run(self):
        while True:
            self.timeout.emit()
            self.sleep(2)

class Monitor(QDialog):
    def __init__(self, parent, timer):
        super().__init__(parent)

        self.setWindowTitle("资源监视器")
        self.setGeometry(100, 100, 400, 300)
        
        # 设置对话框背景颜色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        self.setPalette(palette)
        
        # 使用布局管理小部件
        layout = QVBoxLayout()
        
        # 美化标签
        self.cpu_label = QLabel("CPU使用率: ")
        
        self.cpu_chart = QChart()
        self.cpu_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.cpu_chart.legend().hide()

        self.line_series = QLineSeries(self)  # Using line charts for this example
        self.x_values = [1.0, 2, 3, 4, 5, 6, 7]
        self.y_values = [0, 100, 2, 1, 0, 0, 0]
        
        for value in range(0, len(self.x_values)):
            self.line_series.append(self.x_values[value], self.y_values[value])
            
        self.cpu_chart.addSeries(self.line_series)  # Add line series to chart instance
        
        self.memory_label = QLabel("内存使用率: ")
        self.disk_label = QLabel('磁盘使用率: ')

        # for label in [self.cpu_label, self.memory_label, self.disk_label]:
        #     label.setFont(QFont("Arial", 14))
        #     label.setStyleSheet("color: white; background-color: #444444; padding: 10px; border-radius: 5px;")
        #     layout.addWidget(label)
        # 先添加cpu
        hlayout = QHBoxLayout()
        self.cpu_label.setFont(QFont('Arial', 14))
        self.cpu_label.setStyleSheet("color: white; background-color: #444444; padding: 10px; border-radius: 5px;")
        hlayout.addWidget(self.cpu_label)
        self.cpu_view = QChartView(self.cpu_chart)
        hlayout.addWidget(self.cpu_view)
        
        oneline = QWidget()
        oneline.setLayout(hlayout)
        layout.addWidget(oneline)

        self.setLayout(layout)
        
        self.worker = MyWorker()
        self.worker.timeout.connect(self.update_resources)
        self.worker.start()

    def update_resources(self):
        # cpu_usage = psutil.cpu_percent(interval=1)
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')

        self.cpu_label.setText(f"CPU使用率: {cpu_usage}%")
        # self.y_values.pop(0) 
        # self.y_values.append(cpu_usage)
        
        # self.line_series.clear()
        # for value in range(0, len(self.x_values)):
        #     self.line_series.append(self.x_values[value], self.y_values[value])
            
        # self.cpu_chart.addSeries(self.line_series)  # Add line series to chart instance
        
        
        self.memory_label.setText(f"内存使用率: {memory_info.percent}%")
        self.disk_label.setText(f'磁盘使用率: {(disk_usage.used / disk_usage.total)*100:.1f}%')
        
    def closeEvent(self, event):
        print('关闭')
