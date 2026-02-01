import sys
import os
import qdarktheme
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

def main():  
    app = QApplication(sys.argv)

    # Load your custom CSS
    custom_qss = ""
    qss_path = os.path.join(os.path.dirname(__file__), "css", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            custom_qss = f.read()

    # Apply the theme   
    qdarktheme.setup_theme(
        theme="dark", 
        corner_shape="rounded",
        additional_qss=custom_qss
    )

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()