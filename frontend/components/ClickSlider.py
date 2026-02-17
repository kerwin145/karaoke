from PySide6.QtWidgets import QSlider, QStyle
from PySide6.QtCore import Qt

class ClickSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 1. Calculate the value based on where we clicked
            value = QStyle.sliderValueFromPosition(
                self.minimum(), 
                self.maximum(), 
                event.x(), 
                self.width()
            )
            self.setValue(value)
            
            # 2. Inform the system the slider was moved
            self.sliderMoved.emit(value)
            
            # 3. Prevent the default handler from doing its thing
            event.accept()
        else:
            super().mousePressEvent(event)