from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel)

from components import TrackListWidget, AddSongWidget, MainPlayer

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

        self.track_list = TrackListWidget()

        self.add_song_widget = AddSongWidget(self.track_list)
        
        self.left_column.addWidget(QLabel("Available Tracks"))
        self.left_column.addWidget(self.track_list)
        self.left_column.addWidget(self.add_song_widget)

        # RIGHT COLUMN 3/4 width
        self.right_column = QVBoxLayout()

        self.player_frame = MainPlayer()
        self.right_column.addWidget(self.player_frame)

        # COMBINED LAYOUT
        self.main_layout.addLayout(self.left_column, 1)
        self.main_layout.addLayout(self.right_column, 3)

        # add connectors
        self.track_list.track_selected.connect(self.player_frame.load_track)

        # INITIALIZE CONTENT
        self.track_list.refresh() # api call

   