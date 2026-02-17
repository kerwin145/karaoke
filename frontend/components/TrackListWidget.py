from PySide6.QtWidgets import (QListWidget)
from PySide6.QtCore import Signal
from api_client import get_all_tracks

class TrackListWidget(QListWidget):
    track_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.itemClicked.connect(self._on_item_clicked)
        self.refresh()

    def refresh(self):
        """Fetch tracks from backend and update UI"""
        self.clear()
        tracks = get_all_tracks()

        if tracks:
            self.addItems(tracks)
        else:
            self.addItem("No tracks found or server offline")

    def _on_item_clicked(self, item):
        self.track_selected.emit(item.text())