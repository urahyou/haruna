# code:utf-8
# Create by Maxtang
# 2023/5/3
import psutil
import sys
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QColor, QPalette, QPen
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QPointF
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
            self.sleep(1)

class Monitor(QDialog):
    def __init__(self, parent, timer):
        super().__init__(parent)
        
        self.setWindowTitle("资源监视器")
        # x, y, w, h
        self.setGeometry(100, 100, 1000, 600)
        
        # 设置对话框背景颜色
        self.setAutoFillBackground(True)
        palette = self.palette() # 获取调色板
        palette.setColor(QPalette.Window, QColor(30,30,30))
        self.setPalette(palette)
        
        axis_pen = QPen(QColor(255, 192, 203))  # 粉色
        
        self.lines = {'cpu': QWidget(),
                      'memory': QWidget()}
        
        self.series = {'cpu': QLineSeries(),
                       'memory': QLineSeries()}
        
        self.axis_xs = {'cpu': QValueAxis(),
                        'memory': QValueAxis()}
        
        self.axis_ys = {'cpu': QValueAxis(),
                        'memory': QValueAxis()}
        
        self.charts = {'cpu': QChart(),
                       'memory': QChart()}
        
        self.labels = {'cpu': QLabel(),
                       'memory': QLabel()}
        
        self.chart_views = {'cpu': QChartView(),
                            'memory': QChartView()}
        
        self.datas = {'cpu': [0.0]*60,
                      'memory': [0.0]*60}
        
        self.charts['cpu'].setBackgroundBrush(QColor(25,25,25))  # 设置为深灰色
        self.charts['cpu'].setPlotAreaBackgroundBrush(QColor(25,25,25))
        self.charts['cpu'].setPlotAreaBackgroundVisible(True)
        self.series['cpu'].setColor(QColor(135, 206, 250))  # 浅蓝色
        # 在设置坐标轴之前要把数据先加进去
        self.charts['cpu'].addSeries(self.series['cpu'])

        self.axis_xs['cpu'].setRange(0, 60)
        self.axis_xs['cpu'].setVisible(True)
        self.axis_xs['cpu'].setLabelsVisible(True)
        self.axis_xs['cpu'].setGridLinePen(axis_pen)
        # self.axis_xs['cpu'].setGridLineVisible(False)
        self.axis_xs['cpu'].setLabelFormat('%d')
        self.axis_xs['cpu'].setLinePen(axis_pen)
        self.axis_xs['cpu'].setLabelsColor(QColor(255, 192, 203))
        # self.axis_xs['cpu'].setTitleText('Seconds')
        
        self.axis_ys['cpu'].setRange(0, 100)
        self.axis_ys['cpu'].setVisible(True)
        self.axis_ys['cpu'].setGridLinePen(axis_pen)
        self.axis_ys['cpu'].setLinePen(axis_pen)
       
        self.axis_ys['cpu'].setLabelFormat('%d')
        self.axis_ys['cpu'].setLabelsColor(QColor(255, 192, 203))  # 亮粉色
        self.charts['cpu'].legend().hide()

        self.charts['cpu'].setAxisX(self.axis_xs['cpu'], self.series['cpu'])
        self.charts['cpu'].setAxisY(self.axis_ys['cpu'], self.series['cpu'])
        self.chart_views['cpu'].setChart(self.charts['cpu'])
        self.chart_views['cpu'].setFixedHeight(200)
        self.chart_views['cpu'].setFixedWidth(290)
        
        self.charts['memory'].setBackgroundBrush(QColor(25,25,25))  # 设置为深灰色
        self.charts['memory'].setPlotAreaBackgroundBrush(QColor(25,25,25))
        self.charts['memory'].setPlotAreaBackgroundVisible(True)
        self.series['memory'].setColor(QColor(123, 104, 238))  # 浅紫色
        # 在设置坐标轴之前要把数据先加进去
        self.charts['memory'].addSeries(self.series['memory'])

        self.axis_xs['memory'].setRange(0, 60)
        self.axis_xs['memory'].setVisible(True)
        self.axis_xs['memory'].setLinePen(axis_pen)
        self.axis_xs['memory'].setGridLinePen(axis_pen)
        self.axis_xs['memory'].setLabelFormat('%d')
        self.axis_xs['memory'].setLabelsColor(QColor(255, 192, 203))

    
        self.axis_ys['memory'].setRange(0, 100)
        self.axis_ys['memory'].setVisible(True)
        self.axis_ys['memory'].setLinePen(axis_pen)
        self.axis_ys['memory'].setGridLinePen(axis_pen)
        self.axis_ys['memory'].setLabelFormat('%d')
        self.axis_ys['memory'].setLabelsColor(QColor(255, 192, 203))
        self.charts['memory'].legend().hide()

        self.charts['memory'].setAxisX(self.axis_xs['memory'], self.series['memory'])
        self.charts['memory'].setAxisY(self.axis_ys['memory'], self.series['memory'])
        self.chart_views['memory'].setChart(self.charts['memory'])
        self.chart_views['memory'].setFixedWidth(290)
        self.chart_views['memory'].setFixedHeight(200)
        
        
        self.labels['cpu'].setText('处理器: ')
        self.labels['cpu'].setStyleSheet('color: pink;')
        self.labels['memory'].setText('内存: ')
        self.labels['memory'].setStyleSheet('color: pink;')
        
        self.vlayout = QVBoxLayout()
        
        self.cpu_hlayout = QHBoxLayout()
        self.memory_hlayout = QHBoxLayout()
        
        self.cpu_hlayout.addWidget(self.labels['cpu'])
        self.cpu_hlayout.addWidget(self.chart_views['cpu'])
        self.lines['cpu'].setLayout(self.cpu_hlayout)
        # self.lines['cpu'].setMinimumHeight(200)
        
        self.memory_hlayout.addWidget(self.labels['memory'])
        self.memory_hlayout.addWidget(self.chart_views['memory'])
        self.lines['memory'].setLayout(self.memory_hlayout)
        # self.lines['memory'].setMinimumHeight(200)
        
        self.vlayout.addWidget(self.lines['cpu'])
        self.vlayout.addWidget(self.lines['memory'])
        self.setLayout(self.vlayout)
        
        self.worker = MyWorker()
        self.worker.timeout.connect(self.update_chart)
        self.worker.start()
        
    def update_chart(self):
        # cpu的
        cpu_usage = psutil.cpu_percent()
        self.labels['cpu'].setText(f'处理器: {cpu_usage}%')
        self.datas['cpu'].append(cpu_usage)
        self.datas['cpu'].pop(0)
        # print(self.datas['cpu'])
        self.series['cpu'].clear()
        for i, usage in enumerate(self.datas['cpu']):
            self.series['cpu'].append(QPointF(i, usage))
            
        # memory的
        info = psutil.virtual_memory()
        memory_usage = info.percent
        self.labels['memory'].setText(f'内存: {memory_usage}%')
        self.datas['memory'].append(memory_usage)
        self.datas['memory'].pop(0)
        self.series['memory'].clear()
        for i, usage in enumerate(self.datas['memory']):
            self.series['memory'].append(QPointF(i, usage))
        
            
            
