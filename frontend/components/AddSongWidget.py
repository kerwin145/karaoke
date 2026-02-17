from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QFileDialog)
from PySide6.QtCore import QThread, Signal

from api_client import upload_to_server, check_status, BASE_URL
from .TrackListWidget import TrackListWidget
import time

class AddSongWidget(QWidget):
    add_track = Signal()

    def __init__(self, track_list: TrackListWidget, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.status_label = QLabel("")
        
        self.start_btn = QPushButton("Add New Track")
        self.start_btn.clicked.connect(self.handle_start)

        self.progress = QProgressBar()
        self.progress.hide() # HIDE initially as requested

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.start_btn)
        self.layout.addWidget(self.progress)


        self.track_list = track_list # link to the track list that will refresh when song finishes processing
    
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
            self.track_list.refresh()
        else:
            self.status_label.setText(f"Error: {message}")
            self.status_label.setStyleSheet("color: #f44336;")

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