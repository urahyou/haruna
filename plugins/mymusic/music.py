import sys
from plugins.mymusic import crawler, myui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


# 继承自Ui_MainWindow
class MusicBox(QMainWindow, myui.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 实例化一个 Ui_MainWindow对象
        self.ui= myui.Ui_MainWindow()
       	# setupUi函数
       	# 这个函数很多地方说是初始化ui对象，我觉得直接翻译为“设置UI”
       	# 这样表明ui对象的实例化和设置（或者说加载）是完全不相干的两步
        self.setupUi(self)
        # 这里使用的是 self.show(),和之后的区分一下
        self.searchButton.pressed.connect(self.search)
        self.songsList.doubleClicked.connect(self.song_click) # 双击事件
        #self.searchButton.clicked.connect(self.search) # 两个都是可以的
        self.playButton.clicked.connect(self.switch)
        #self.playButton.setStyleSheet('border-radius: 50%')
        self.playButton.setIcon(QIcon('icons/play.png')) # 初始化图标
        self.player = QMediaPlayer() # 初始化播放器
        self.nextButton.clicked.connect(self.next)
        self.previousButton.clicked.connect(self.previous)
        # 大小是从0到100
        self.songSlider.sliderMoved.connect(self.sliderDrag)
        self.soundSlider.setMinimum(0)
        self.soundSlider.setMaximum(100)
        self.soundSlider.sliderMoved.connect(self.songDrag)
        self.setStyleSheet('background-color: #c95762')
        self.timer = QTimer(self)
        self.playedTime = 0  # 已播放时间
        self.totlaTime = 0   # 当前歌曲的时间总长，以ms为单位
        self.show()     
    
       
    def switch(self):
        print(self.player.state())
        # 播放状态
        if self.player.state() == QMediaPlayer.State.PlayingState:
            self.player.pause()
            self.playButton.setIcon(QIcon('icons/play.png'))
        # 暂停状态
        elif self.player.state() == QMediaPlayer.State.PausedState:
            self.player.play()
            self.playButton.setIcon(QIcon('icons/pause.png'))
        
    
    def song_click(self):
        # print(self.songsList.currentItem().text())
        #print(self.songsList.currentRow())  # 当前选中的行
        self.song_play()
    
    
    def song_play(self):
        self.player.stop() 
        self.player.setMedia(QMediaContent()) # 这样才能解除已经播放过的文件占用问题
        row = self.songsList.currentRow()
        song_name = self.songs[row]['name']
        song_id = self.songs[row]['id']
        mp3 = crawler.download_song(song_name, song_id)
        if mp3 is None:
            print('歌曲无法播放')
            return
        file = open('songs/tmp.mp3', mode='wb+') 
        file.write(mp3)
        file.close()
        # 加载要播放的文件
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile('songs/tmp.mp3')))
        self.player.setVolume(10) # 设置音量
        self.player.play()  # 开始播放
        self.totlaTime = self.songsDuration[row]
        self.label.setText(song_name) # 设置播放的名字
        self.label_2.setText(self.songsDuration1[row])
        self.playButton.setIcon(QIcon('icons/pause.png'))    
        self.timer_start() # 开始计时，绑定进度条操作
    
    
    def closeEvent(self, event):
        self.timer.stop()
        print('计时器关闭成功')
        self.player.stop()
        print('音乐播放器关闭成功')
                
    
    def next(self):
        self.songsList.setCurrentRow(self.songsList.currentRow() + 1)
        self.song_play()
    

    def previous(self):
        self.songsList.setCurrentRow(self.songsList.currentRow() - 1)
        self.song_play()
    
    
    def search(self):
        name = self.searchBox.text()
        self.songs = crawler.search_song(name, return_limit=20)
        self.songsList.clear()
        self.songsDuration = []
        self.songsDuration1 = []
        for song in self.songs:  
            name = song['name']
            duration = song['duration'] / 1000 # ms -> s
            m, s = divmod(duration, 60) # 获取分、秒
            duration = '{:02d}:{:02d}'.format(int(m),int(s))
            self.songsDuration.append(song['duration']) # ms*1000制
            self.songsDuration1.append(duration) # m,s制
            self.songsList.addItem(song['name'])
        
        
    def timer_start(self):
        self.timer.start(1000) # 每1000ms / 1s 刷新一次
        self.timer.timeout.connect(self.update_slider)
        self.songSlider.setMaximum(self.totlaTime)
        self.songSlider.setMinimum(0)  
        self.songSlider.setValue(0)
     
     
    def update_slider(self):
        # 每隔1s刷新一次
        #self.songSlider.setValue(self.songSlider.value() + 1000)
        print(self.player.position())
        self.songSlider.setValue(self.player.position())


    def sliderDrag(self):
        print(self.songSlider.value())
        self.player.setPosition(self.songSlider.value())


    def songDrag(self):
        self.player.setVolume(self.soundSlider.value())


# 作为模块导入的时候，这个是不会执行的
if __name__=="__main__":
    app=QApplication(sys.argv)
    window=MusicBox()
    sys.exit(app.exec_())
