from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton, QFrame, QSizePolicy

from PySide6.QtCore import QEasingCurve, QPropertyAnimation

class AddLyricsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent) 
        
        self.setMaximumWidth(0)   # start collapsed/hidden
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(QLabel("Add Lyrics"))

        self.text_box = QPlainTextEdit()
        self.text_box.setPlaceholderText("Paste or type lyrics here...")
        layout.addWidget(self.text_box)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self._on_submit)
        layout.addWidget(self.submit_btn)

        self._panel_open = False
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

    def toggle(self):
        """Slot — connect player_frame's signal to this."""
        self._panel_open = not self._panel_open
        self._anim.setStartValue(self.maximumWidth())
        self._anim.setEndValue(250 if self._panel_open else 0)
        self._anim.start()

    def _on_submit(self):
        text = self.text_box.toPlainText().strip()
        if text:
            pass  # downstream logic TBD