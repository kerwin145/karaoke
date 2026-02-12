from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QProgressBar, QLabel, QFileDialog, 
                             QListWidget, QSlider, QFrame, QStyle)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from api_client import upload_to_server, check_status, get_all_tracks, BASE_URL
from components.ClickSlider import ClickSlider

import time

class ProcessingWorker(QThread):
    finished = Signal(bool, str)
    status_update = Signal(str) # allows updating of UI text during status polling

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            # Talk to the FastAPI server
            self.status_update.emit("Uploading to Server...")
            init_res = upload_to_server(self.file_path)
            task_id = init_res.get("task_id")

            if not task_id:
                self.finished.emit(False, "Failed to start task on server.")
                return
            
            while True:
                res = check_status(task_id)
                status = res.get("status")
                
                if status == "completed":
                    self.finished.emit(True, res.get("message", "Done!"))
                    break
                elif status == "failed":
                    self.finished.emit(False, res.get("message", "GPU Error"))
                    break
                
                # Update UI and wait 2 seconds before asking again
                self.status_update.emit("AI is separating tracks")
                time.sleep(2)

        except Exception as e:
            self.finished.emit(False, f"Connection Error: {str(e)}")
            
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karaoke")
        self.resize(1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # LEFT SECTION 1/4 width
        self.left_column = QVBoxLayout()

        self.track_list = QListWidget()
        self.track_list.itemClicked.connect(self.load_track)

        self.status_label = QLabel("")
        
        self.start_btn = QPushButton("Add New Track")
        self.start_btn.clicked.connect(self.handle_start)

        self.progress = QProgressBar()
        self.progress.hide() # HIDE initially as requested
        
        self.left_column.addWidget(QLabel("Available Tracks"))
        self.left_column.addWidget(self.track_list)
        self.left_column.addWidget(self.status_label)
        self.left_column.addWidget(self.progress)
        self.left_column.addWidget(self.start_btn)

        # RIGHT COLUMN 3/4 width
        self.right_column = QVBoxLayout()
        self.player_frame = QFrame()
        self.player_frame.setFrameShape(QFrame.StyledPanel)
        self.player_layout = QVBoxLayout(self.player_frame)
        
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

        ## Add the frame to the right column
        self.right_column.addWidget(self.player_frame)

        # COMBINED LAYOUT
        self.main_layout.addLayout(self.left_column, 1)
        self.main_layout.addLayout(self.right_column, 3)

        # INITIALIZE CONTENT
        self.refresh_ui_list() # api call

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
        
    def load_track(self, item):
        song_name = item.text()
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

    def refresh_ui_list(self):
        tracks = get_all_tracks() # using the new api_client function
        self.track_list.clear()
        if tracks:
            self.track_list.addItems(tracks)
        else:
            self.track_list.addItem("No tracks found or server offline")

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

    # For asynchronous video uploading 
    def handle_start(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video (*.mp4 *.mkv)")
        if path:
            self.start_btn.setEnabled(False)
            self.progress.show() # SHOW when processing starts
            self.progress.setRange(0, 0) 
            self.status_label.setText("Uploading to Backend...")
            
            self.worker = ProcessingWorker(path)
            self.worker.status_update.connect(lambda msg: self.status_label.setText(msg))
            self.worker.finished.connect(self.on_complete)
            self.worker.start()

    def on_complete(self, success, message):
        self.start_btn.setEnabled(True)
        self.progress.hide() # HIDE when finished
        
        if success:
            self.status_label.setText("Processing Complete!")
            self.status_label.setStyleSheet("color: #4CAF50;")
            self.refresh_ui_list()
        else:
            self.status_label.setText(f"Error: {message}")
            self.status_label.setStyleSheet("color: #f44336;")