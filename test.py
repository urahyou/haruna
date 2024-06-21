import sys
import psutil
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

class NetworkMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.setGeometry(100, 100, 1000, 600)

        self.upload_series = QLineSeries()
        self.download_series = QLineSeries()

        # Initialize charts
        self.init_network_chart()

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.network_chart_view)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Set up timer to update data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second

        # Initialize previous data
        self.previous_upload = 0
        self.previous_download = 0

    def init_network_chart(self):
        self.network_chart = QChart()
        self.network_chart.addSeries(self.upload_series)
        self.network_chart.addSeries(self.download_series)
        self.network_chart.setTitle("Network Usage (KB/s)")

        self.network_axis_x = QValueAxis()
        self.network_axis_x.setRange(0, 60)
        self.network_axis_x.setLabelFormat("%d")
        self.network_axis_x.setLabelsColor(QColor(255, 192, 203))  # Pink
        self.network_axis_x.setGridLinePen(QPen(QColor(255, 192, 203)))  # Pink

        self.network_axis_y = QValueAxis()
        self.network_axis_y.setRange(0, 1000)
        self.network_axis_y.setLabelFormat("%d")
        self.network_axis_y.setLabelsColor(QColor(255, 192, 203))  # Pink
        self.network_axis_y.setGridLinePen(QPen(QColor(255, 192, 203)))  # Pink

        self.network_chart.addAxis(self.network_axis_x, Qt.AlignBottom)
        self.network_chart.addAxis(self.network_axis_y, Qt.AlignLeft)
        self.upload_series.attachAxis(self.network_axis_x)
        self.upload_series.attachAxis(self.network_axis_y)
        self.download_series.attachAxis(self.network_axis_x)
        self.download_series.attachAxis(self.network_axis_y)

        self.upload_series.setColor(QColor(255, 99, 132))  # Pink
        self.download_series.setColor(QColor(54, 162, 235))  # Blue

        self.network_chart_view = QChartView(self.network_chart)
        self.network_chart_view.setRenderHint(QPainter.Antialiasing)

    def update_data(self):
        net_io = psutil.net_io_counters()

        if self.previous_upload == 0 or self.previous_download == 0:
            self.previous_upload = net_io.bytes_sent
            self.previous_download = net_io.bytes_recv
            return

        upload_speed = (net_io.bytes_sent - self.previous_upload) / 1024  # KB/s
        download_speed = (net_io.bytes_recv - self.previous_download) / 1024  # KB/s

        self.previous_upload = net_io.bytes_sent
        self.previous_download = net_io.bytes_recv

        if len(self.upload_series) >= 60:
            self.upload_series.remove(0)
        self.upload_series.append(len(self.upload_series), upload_speed)

        if len(self.download_series) >= 60:
            self.download_series.remove(0)
        self.download_series.append(len(self.download_series), download_speed)

        self.network_axis_y.setRange(0, max(max([p.y() for p in self.upload_series.points()]), max([p.y() for p in self.download_series.points()]), 1000))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkMonitor()
    window.show()
    sys.exit(app.exec_())
