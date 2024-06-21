import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QSlider
from PyQt5.QtCore import Qt, QTimer
from pygame import mixer

class MP3Player(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        mixer.init()
        self.is_paused = False

    def initUI(self):
        self.setWindowTitle('MP3 Player')
        self.setGeometry(300, 300, 300, 150)
        
        layout = QVBoxLayout()

        self.label = QLabel('No file loaded', self)
        layout.addWidget(self.label)
        
        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_music)
        layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton('Pause', self)
        self.pause_button.clicked.connect(self.pause_music)
        layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_music)
        layout.addWidget(self.stop_button)
        
        self.load_button = QPushButton('Load', self)
        self.load_button.clicked.connect(self.load_music)
        layout.addWidget(self.load_button)
        
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.set_volume)
        layout.addWidget(self.slider)
        
        self.setLayout(layout)
        
    def load_music(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open MP3 File", "", "MP3 Files (*.mp3);;All Files (*)", options=options)
        if file_name:
            self.label.setText(file_name)
            mixer.music.load(file_name)
        
    def play_music(self):
        if self.is_paused:
            mixer.music.unpause()
            self.is_paused = False
        else:
            mixer.music.play()
        
    def pause_music(self):
        mixer.music.pause()
        self.is_paused = True
        
    def stop_music(self):
        mixer.music.stop()
        self.is_paused = False

    def set_volume(self, value):
        volume = value / 100
        mixer.music.set_volume(volume)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MP3Player()
    player.show()
    sys.exit(app.exec_())
