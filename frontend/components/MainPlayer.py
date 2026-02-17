from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QSlider, QFrame, QStyle)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from components import ClickSlider 
from api_client import BASE_URL

class MainPlayer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.StyledPanel)
        self.player_layout = QVBoxLayout(self)

        self.song_title = QLabel("Select a track to play")
        self.song_title.setAlignment(Qt.AlignCenter)
        self.song_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        ## Playback controls
        self.controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_playback)
        
        self.seek_slider = ClickSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderMoved.connect(self.set_position)
        
        self.controls_layout.addWidget(self.play_btn)
        self.controls_layout.addWidget(self.seek_slider)

        ## Volume Controls
        self.vocal_vol = self.create_volume_slider("Vocal Volume", "vocal")
        self.inst_vol = self.create_volume_slider("Instrumental Volume", "inst")
        
        ## Video 
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(400) # Give the video some space

        ### Assemble
        self.player_layout.insertWidget(0, self.video_widget) # Place video at the top
        self.player_layout.addStretch()
        self.player_layout.addWidget(self.song_title)
        self.player_layout.addLayout(self.controls_layout)
        self.player_layout.addStretch()
        self.player_layout.addLayout(self.vocal_vol)
        self.player_layout.addLayout(self.inst_vol)

        ### Setting up audio and video output
        self.vocal_player = QMediaPlayer()
        self.vocal_output = QAudioOutput()
        self.vocal_player.setAudioOutput(self.vocal_output)
        
        self.inst_player = QMediaPlayer()
        self.inst_output = QAudioOutput()
        self.inst_player.setAudioOutput(self.inst_output)

        self.video_player = QMediaPlayer()
        self.video_player.setVideoOutput(self.video_widget)

        ### Connect players to the seeker. We use inst_player as the "master" for timing
        self.inst_player.positionChanged.connect(self.update_position)
        self.inst_player.durationChanged.connect(self.update_duration)
        self.inst_player.playbackStateChanged.connect(self.update_buttons)

    def create_volume_slider(self, label_text, player_type):
        layout = QVBoxLayout()
        label = QLabel(label_text)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100) 

        if player_type == "vocal":
            slider.setValue(50)
            slider.valueChanged.connect(lambda v: self.vocal_output.setVolume(v / 100))
        else:
            slider.setValue(100)
            slider.valueChanged.connect(lambda v: self.inst_output.setVolume(v / 100))

        layout.addWidget(label)
        layout.addWidget(slider)

        return layout
        
    def load_track(self, song_name):
        self.song_title.setText(f"Playing: {song_name}")
        
        # Construct URLs to the backend static mount
        vocal_url = f"{BASE_URL}/audio/{song_name}/vocals.wav"
        inst_url = f"{BASE_URL}/audio/{song_name}/no_vocals.wav"
        video_url = f"{BASE_URL}/video/{song_name}"

        self.vocal_player.setSource(QUrl(vocal_url))
        self.inst_player.setSource(QUrl(inst_url))
        self.video_player.setSource(QUrl(video_url))

        self.vocal_player.play()
        self.inst_player.play()
        self.video_player.play()

    def toggle_playback(self):
        # Both players stay in sync by sharing the same command
        if self.inst_player.playbackState() == QMediaPlayer.PlayingState:
            self.vocal_player.pause()
            self.inst_player.pause()
            self.video_player.pause()
        else:
            self.vocal_player.play()
            self.inst_player.play()
            self.video_player.play()

    def update_buttons(self, state):
        # Changes icon based on whether the music is moving or not
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def update_duration(self, duration):
        # Sets the slider max when a new song loads
        self.seek_slider.setRange(0, duration)

    def update_position(self, position):
        # Moves the slider as the song plays
        self.seek_slider.setValue(position)

    def set_position(self, position):
        # Allows user to click/drag slider to change time for BOTH tracks
        self.vocal_player.setPosition(position)
        self.inst_player.setPosition(position)
        self.video_player.setPosition(position)



