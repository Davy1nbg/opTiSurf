import sys
from PyQt6.QtWidgets import QApplication

# Importiere die MainWindow-Klasse aus der main_window.py Datei
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # Das .show() wird bereits im __init__ von MainWindow aufgerufen
    sys.exit(app.exec())