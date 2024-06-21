from PyQt5.QtGui import QPixmap, QBitmap, QIcon, QCursor
from PyQt5.QtCore import  Qt, QTimer
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QSystemTrayIcon, QMenu, QMessageBox, QWidget
import sys
from plugins.weather import weather
from plugins.notebook.mynotebook import MyNoteBook
from plugins.monitor.monitor import  Monitor
from plugins.mymusic import MusicBox



class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        # 设置背景透明
        #self.setStyleSheet('QMenu {background-color: #660000; color: white;}')
        #self.setStyleSheet('QMessageBox {background-color: black; color: white;}')
        self.setWindowFlags(Qt.FramelessWindowHint) # 设置成无边框
        self.setAutoFillBackground(True)   # 自动填充背景
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # type: ignore
        self.image = QLabel(self)
        self.poses = [QPixmap('shell/surface/surface0000.png'), QPixmap('shell/surface/surface0033.png')]
        self.pose_idx = 0
        self.pic = self.poses[self.pose_idx]
        self.mymask = QBitmap('shell/mymask.png')
        
        self.pic.setMask(self.mymask)
        self.image.setPixmap(self.pic)
        self.resize(self.pic.size())
        
        self.update()
        
        # 设置定时器
        self.timer = QTimer(self)
        # self.timer.timeout.connect(self.switchPose)
        # self.timer.start(2000)ls
        
        # 设置托盘
        # self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon('tigerIcon.jpg'))
        # # 托盘菜单
        # self.tray_icon_menu = QMenu(self)
        # quit_action = QAction(text='退出', parent=self, triggered=self.close)  
        # show_action = QAction(text='显示', parent=self, triggered=self.showwin)
    
        # self.tray_icon_menu.addAction(quit_action)
        # self.tray_icon_menu.addAction(show_action)
        # # 添加上下文菜单
        # self.tray_icon.setContextMenu(self.tray_icon_menu)
        # self.tray_icon.show()
        
        
    def mousePressEvent(self, event):
        self.is_follow_mouse = False
        # 按下了鼠标左键
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            # 表示事件已经处理，不需要再向父窗口传播
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
        self.update()


    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
        event.accept()
        self.update()

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.update()
        
    def enterEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        self.update()
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        weatherAction = menu.addAction('天气')
        notebookAction = menu.addAction('日记')
        musicAction = menu.addAction('音乐')
        monitorAction = menu.addAction('资源监控')
        hideAction = menu.addAction('隐藏')
        quitAction = menu.addAction('退出')
        # 使用exec_()方法显示菜单。从鼠标右键事件对象中获得当前坐标。
        # mapToGlobal()方法把当前组件的相对坐标转换为窗口（window）的绝对坐标。
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == quitAction:
            # PyQt5.QtWidgets.qApp
            #qApp.quit()
            # 下面这个也可以，更简洁
            self.close()
        elif action == hideAction:
            #self.setWindowOpacity(0)
            self.hide()
        elif action == weatherAction:
            self.showWeather()
        elif action == notebookAction:
            self.showNotebook()
        elif action == musicAction:
            self.showMusicBox()
        elif action == monitorAction:
            self.showMonitor()
    
    # 换姿势
    def switchPose(self):
        if self.pose_idx == 1:
            self.pose_idx = 0
        else:
            self.pose_idx = 1
        self.pic = self.poses[self.pose_idx]
        self.pic.setMask(self.mymask)
        self.image.setPixmap(self.pic)
        self.resize(self.pic.size())
        
    # 显示主体
    def showwin(self):
        #self.setWindowOpacity(1)
        self.show()
       
    # 打开天气预报
    def showWeather(self):
        msgBox = QMessageBox(self)
        msgBox.setStyleSheet('background-color: black; color: white')
        msgBox.setModal(False) # 非模态窗口，也就是不会强制聚焦
        msgBox.move(self.x()+self.width(), self.y())
        msgBox.setWindowTitle('天气预报')
        msgBox.setText('<h2>广州天气</h2>')
        #msgBox.setWindowOpacity(0.7)
        #msgBox.open()  #show和open都可以
        msgBox.setInformativeText(f'气温范围：loading...\n天气：loading...\n ')
        msgBox.show()
        current_weather = weather.get_weather_by_loc('guangzhou')
        msgBox.setInformativeText('气温范围：{}\n天气：{}\n '.format(current_weather['temp_range'], current_weather['cloud']))
     
    # 打开计事本
    def showNotebook(self):
        notebook = MyNoteBook(self)
        notebook.move(self.x()+self.width(), self.y())
        notebook.show()
    
    # 打开音乐盒
    def showMusicBox(self):
        musicbox = MusicBox(self)
        musicbox.move(self.x()+self.width(), self.y())
        musicbox.show()
        
    # 打开资源监控
    def showMonitor(self):
        monitor = Monitor(self, self.timer) # 把timer 传给子线程
        monitor.move(self.x()+self.width(), self.y())
        monitor.show()

     
if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())
    
    

