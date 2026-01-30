from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QProgressBar, QLabel, QFileDialog)
from PySide6.QtCore import QThread, Signal, Qt
from audio_processing import run_karaoke_process

# This is like a "Custom Hook" for long-running GPU tasks
class ProcessingWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        # Your heavy GPU task runs here in the background
        success, message = run_karaoke_process(self.file_path)
        self.finished.emit(success, message)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Karaoke Creator Pro")
        self.resize(500, 300)

        # Main Layout (Think: <div class="container">)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.status_label = QLabel("Ready to process")
        self.progress = QProgressBar()
        self.start_btn = QPushButton("Select Video & Start")

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.start_btn)

        # Event listeners (Signals/Slots)
        self.start_btn.clicked.connect(self.handle_start)

    def handle_start(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video (*.mp4)")
        if path:
            self.start_btn.setEnabled(False)
            self.progress.setRange(0, 0) # Infinite spinner
            self.status_label.setText("AI is working on GPU...")
            
            # Start background worker
            self.worker = ProcessingWorker(path)
            self.worker.finished.connect(self.on_complete)
            self.worker.start()

    def on_complete(self, success, message):
        self.start_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        
        if success:
            self.status_label.setText(f"Success! {message}")
            self.status_label.setStyleSheet("color: #4CAF50;") # Green for success
        else:
            # This is the key change: display the actual error 'message'
            self.status_label.setText(f"Error: {message}")
            self.status_label.setStyleSheet("color: #f44336;") # Red for error
            print(f"Full Error Trace: {message}")