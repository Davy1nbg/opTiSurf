import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
# from PyQt6.QtWebEngineCore import QWebEngineProfile # Vorerst nicht zwingend nötig

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("opTiSurf Browser") # Name aktualisiert!

        # Adressleiste erstellen
        self.address_bar = QLineEdit()
        # Wenn Enter gedrückt wird in der Adressleiste, rufe navigate_to_url auf
        self.address_bar.returnPressed.connect(self.navigate_to_url)

        # QWebEngineView erstellen
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://example.com"))
        # Wenn die URL sich ändert (z.B. durch Klick auf einen Link), aktualisiere die Adressleiste
        self.browser.urlChanged.connect(self.update_address_bar)

        # Layout erstellen
        layout = QVBoxLayout()
        layout.addWidget(self.address_bar) # Adressleiste oben
        layout.addWidget(self.browser)     # Browser-Ansicht darunter
        # Wichtig: Setze den Abstand zwischen Widgets und um das Layout herum auf 0
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        # Ein zentrales Widget erstellen, um das Layout aufzunehmen
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.resize(1024, 768)
        self.show()

    def navigate_to_url(self):
        # Hole die URL aus der Adressleiste
        url_text = self.address_bar.text()

        # Einfache Überprüfung und Ergänzung des Schemas (http/https)
        if not url_text.startswith("http://") and not url_text.startswith("https://"):
            # Versuche https, da es bevorzugt wird
            url_text = "https://" + url_text
        
        # Setze die neue URL im Browser-Widget
        self.browser.setUrl(QUrl(url_text))

    def update_address_bar(self, qurl):
        # Aktualisiere den Text in der Adressleiste mit der aktuellen URL der Webseite
        # qurl ist ein QUrl Objekt, .toString() gibt den String zurück
        self.address_bar.setText(qurl.toString())
        # Setze den Cursor an den Anfang der Adressleiste (optional, für bessere Usability)
        self.address_bar.setCursorPosition(0)


# QApplication initialisieren
app = QApplication(sys.argv)

# Hauptfenster erstellen und anzeigen
window = MainWindow()

# Event-Loop der Anwendung starten
sys.exit(app.exec())