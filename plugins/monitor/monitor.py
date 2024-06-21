# code:utf-8
# Create by Maxtang
# 2023/5/3
import psutil
import sys
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QColor, QPalette, QPen, QBrush, QPainter
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QPointF, Qt
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QPieSeries
import numpy as np

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
            self.sleep(1) # 1s更新一次

class Monitor(QDialog):
    def __init__(self, parent, timer):
        super().__init__(parent)
        
        self.setWindowTitle("资源监视器")
        # x, y, w, h
        # self.setGeometry(100, 100, 1000, 600)
        
        # 设置对话框背景颜色
        self.setAutoFillBackground(True)
        palette = self.palette() # 获取调色板
        palette.setColor(QPalette.Window, QColor(30,30,30))
        self.setPalette(palette)
        
        self.cpu_datas = [0.0]*60
        self.memory_datas = [0.0]*60
        self.upload_datas = [0.0]*60
        self.download_datas = [0.0]*60
        self.previous_upload = 0
        self.previous_download = 0

        self.pink_color = QColor(255, 192, 203)
        
        layout = QHBoxLayout()
        layout.setSpacing(0)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        # 左边的布局
        left_layout.addWidget(self.init_cpu_chart())
        left_layout.addWidget(self.init_memory_chart())
        
        # 右边的布局
        right_layout.addWidget(self.init_disk_chart())
        right_layout.addWidget(self.init_network_chart())
        
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        self.setLayout(layout)
        self.timer = MyWorker()
        self.timer.timeout.connect(self.update_data)
        self.timer.start()
   
    
    def init_network_chart(self):
        self.network_chart = QChart()
        self.network_chart.resize(400, 300)
        self.up_speed_series = QLineSeries() # 存放上传速度的数据
        self.up_speed_series.setName('up')
        self.down_speed_series = QLineSeries() # 存放下载速度的数据
        self.down_speed_series.setName('down')
        self.network_chart.addSeries(self.up_speed_series)
        self.network_chart.addSeries(self.down_speed_series)
        self.network_chart.setTitle('Network Usage')
        self.network_chart.setBackgroundBrush(QColor(50, 50, 50))
        # self.network_chart.legend().hide() # 隐藏标签
        self.network_chart.setTitleBrush(self.pink_color)
        self.network_chart.legend().setLabelColor(QColor(150, 150, 150))
        
        self.network_axis_x = QValueAxis()
        self.network_axis_x.setRange(0, 60) # 监控近一分钟的网络的流量
        self.network_axis_x.setLabelFormat('%d')
        self.network_axis_x.setLabelsColor(self.pink_color)
        self.network_axis_x.setGridLinePen(QPen(self.pink_color))
        self.network_axis_x.setLinePen(self.pink_color)
        
        self.network_axis_y = QValueAxis()
        self.network_axis_y.setRange(0, 100)
        self.network_axis_y.setLabelFormat('%d')
        self.network_axis_y.setLabelsColor(self.pink_color)
        self.network_axis_y.setGridLinePen(QPen(self.pink_color))
        self.network_axis_y.setLinePen(self.pink_color)
        
        # 要同时绑定两条轴
        self.network_chart.addAxis(self.network_axis_x, Qt.AlignmentFlag.AlignBottom)
        self.network_chart.addAxis(self.network_axis_y, Qt.AlignmentFlag.AlignLeft)
        self.up_speed_series.attachAxis(self.network_axis_x)
        self.up_speed_series.attachAxis(self.network_axis_y)
        self.down_speed_series.attachAxis(self.network_axis_x)
        self.down_speed_series.attachAxis(self.network_axis_y)
        
        self.up_speed_series.setColor(self.pink_color)
        self.down_speed_series.setColor(QColor(54, 162, 235))
        
        self.network_chart_view = QChartView(self.network_chart)
        self.network_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return self.network_chart_view
        
    def init_cpu_chart(self):
        self.cpu_chart = QChart()
        self.cpu_chart.resize(400, 300)
        self.cpu_series = QLineSeries()
        self.cpu_series.setName('CPU: ')
        self.cpu_chart.addSeries(self.cpu_series)
        self.cpu_chart.setTitle('CPU Usage')
        self.cpu_chart.setTitleBrush(self.pink_color) # 标题的颜色
        self.cpu_chart.legend().setLabelColor(QColor(150,150,150))
        # self.cpu_chart.legend().hide()
        
        self.cpu_axis_x = QValueAxis()
        self.cpu_axis_x.setRange(0, 60)
        self.cpu_axis_x.setLabelFormat('%d') # 只显示一位数字
        self.cpu_axis_x.setLabelsColor(self.pink_color)
        self.cpu_axis_x.setGridLinePen(QPen(self.pink_color))
        self.cpu_axis_x.setLinePen(QPen(self.pink_color))
        
        self.cpu_axis_y = QValueAxis()
        self.cpu_axis_y.setRange(0, 100)
        self.cpu_axis_y.setLabelFormat('%d')
        self.cpu_axis_y.setLabelsColor(self.pink_color)
        self.cpu_axis_y.setGridLinePen(QPen(self.pink_color))
        self.cpu_axis_y.setLinePen(QPen(self.pink_color))
        
        self.cpu_chart.setAxisX(self.cpu_axis_x, self.cpu_series)
        self.cpu_chart.setAxisY(self.cpu_axis_y, self.cpu_series)
        self.cpu_chart.setBackgroundBrush(QColor(50, 50, 50)) # 背景深灰色
        
        self.cpu_series.setColor(QColor(123, 104, 238))
        
        self.cpu_chart_view = QChartView(self.cpu_chart)
        self.cpu_chart_view.setFixedSize(400, 300)
        return self.cpu_chart_view
        
        
    def init_memory_chart(self):
        self.memory_chart = QChart()
        self.memory_series = QLineSeries()
        self.memory_series.setName('Mem: ')
        self.memory_chart.addSeries(self.memory_series)
        self.memory_chart.setTitle('Memory Usage')
        self.memory_chart.setTitleBrush(self.pink_color)
        self.memory_chart.legend().setLabelColor(QColor(150,150,150))
        
        self.memory_axis_x = QValueAxis()
        self.memory_axis_x.setRange(0, 60)
        self.memory_axis_x.setLabelFormat('%d') # 只显示一位数字
        self.memory_axis_x.setLabelsColor(self.pink_color)
        self.memory_axis_x.setGridLinePen(QPen(self.pink_color))
        self.memory_axis_x.setLinePen(QPen(self.pink_color))
        
        self.memory_axis_y = QValueAxis()
        self.memory_axis_y.setRange(0, 100)
        self.memory_axis_y.setLabelFormat('%d')
        self.memory_axis_y.setLabelsColor(self.pink_color)
        self.memory_axis_y.setGridLinePen(QPen(self.pink_color))
        self.memory_axis_y.setLinePen(QPen(self.pink_color))
        
        self.memory_chart.setAxisX(self.memory_axis_x, self.memory_series)
        self.memory_chart.setAxisY(self.memory_axis_y, self.memory_series)
        self.memory_chart.setBackgroundBrush(QColor(50, 50, 50)) # 背景深灰色
        
        self.memory_series.setColor(QColor(123, 104, 238))
        
        self.memory_chart_view = QChartView(self.memory_chart)
        self.memory_chart_view.setFixedSize(400, 300)
        return self.memory_chart_view
        
        
    def init_disk_chart(self):
        disk_usage = psutil.disk_usage('/')
        used = disk_usage.used / (1024 ** 3) # GB
        free = disk_usage.free / (1024 ** 3) # GB
        
        self.disk_pie_series = QPieSeries()
        self.disk_pie_series.append(f'Used: {used:.2f} GB', used)
        self.disk_pie_series.append(f'Free: {free:.2f} GB', free)
        
        slice_used = self.disk_pie_series.slices()[0]
        slice_used.setBrush(QColor(255, 99, 132))  # Pink
    
        slice_free = self.disk_pie_series.slices()[1]
        slice_free.setBrush(QColor(54, 162, 235))  # Blue
        
        self.disk_chart = QChart()
        self.disk_chart.addSeries(self.disk_pie_series)
        self.disk_chart.setTitle("Disk Usage")
        self.disk_chart.setTitleBrush(self.pink_color)
        self.disk_chart.setBackgroundBrush(QColor(50, 50, 50))
        self.disk_chart.legend().setLabelColor(QColor(150,150,150))
        
        self.disk_chart_view = QChartView(self.disk_chart)
        self.disk_chart_view.setRenderHint(QPainter.Antialiasing)
        self.disk_chart_view.setFixedSize(400, 300)
        return self.disk_chart_view
        
        
    def update_data(self):
        # cpu
        cpu_usage = psutil.cpu_percent()
        self.cpu_datas.pop(0)
        self.cpu_datas.append(cpu_usage)
        self.cpu_series.clear()
        for i, usage in enumerate(self.cpu_datas):
            self.cpu_series.append(QPointF(i, usage))
        self.cpu_series.setName(f'CPU: {cpu_usage}%')
            
        # memory
        memory_usage = psutil.virtual_memory().percent
        self.memory_datas.pop(0)
        self.memory_datas.append(memory_usage)
        self.memory_series.clear()
        for i, usage in enumerate(self.memory_datas):
            self.memory_series.append(QPointF(i, usage))
        self.memory_series.setName(f'MEM: {memory_usage}%')
            
        # network
        network = psutil.net_io_counters()
        self.download_datas.pop(0)
        if self.previous_download != 0 :
            down_speed = (network.bytes_recv - self.previous_download) / 1024 
        else:
            down_speed = 0
        self.download_datas.append(down_speed) # KB/s
        self.previous_download = network.bytes_recv
        self.down_speed_series.setName(f'DOWN: {down_speed} KB/s')
        
        self.upload_datas.pop(0)
        if self.previous_upload != 0:
            up_speed = (network.bytes_sent - self.previous_upload) / 1024
        else:
            up_speed = 0
        self.upload_datas.append(up_speed) # KB/s
        self.previous_upload = network.bytes_sent
        self.up_speed_series.setName(f'UP: {up_speed} KB/s')

        self.down_speed_series.clear()
        self.up_speed_series.clear()
        
        max_up = max(self.upload_datas)
        if max_up > 0:
            max_up = 10**(int(np.log10(max_up))+1)
            self.network_axis_y.setRange(0, max_up)
        
        for i, usage in enumerate(self.download_datas):
            self.down_speed_series.append(QPointF(i, usage))
            
        for i, usage in enumerate(self.upload_datas):
            self.up_speed_series.append(QPointF(i, usage))
        
        
        # disk
        disk_usage = psutil.disk_usage('/')
        used = disk_usage.used / (1024 ** 3) # GB
        free = disk_usage.free / (1024 ** 3) # GB
        
        self.disk_pie_series = QPieSeries()
        self.disk_pie_series.append(f'Used: {used:.2f} GB', used)
        self.disk_pie_series.append(f'Free: {free:.2f} GB', free)