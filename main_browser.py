import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView # Wichtig für die Webansicht
from PyQt6.QtWebEngineCore import QWebEngineProfile # Für Profileinstellungen (optional für den Anfang)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Fenstertitel setzen
        self.setWindowTitle("Mein Erster Browser")

        # QWebEngineView erstellen - das ist unser "Browserfenster"
        self.browser = QWebEngineView()

        # Eine Standard-URL laden
        # Du kannst hier jede beliebige URL eintragen, z.B. "https://www.google.com"
        # oder eine lokale HTML-Datei mit "file:///C:/pfad/zu/deiner/datei.html"
        self.browser.setUrl(QUrl("https://example.com")) 

        # Den Webview als zentrales Widget des Hauptfensters setzen
        self.setCentralWidget(self.browser)

        # Fenstergröße initial setzen (optional)
        self.resize(1024, 768)

        # Fenster anzeigen
        self.show()

# QApplication initialisieren (notwendig für jede Qt-Anwendung)
app = QApplication(sys.argv)

# Hauptfenster erstellen und anzeigen
window = MainWindow()

# Event-Loop der Anwendung starten
# sys.exit(app.exec()) sorgt für ein sauberes Beenden
sys.exit(app.exec())