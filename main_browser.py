import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout, # Neu für horizontales Layout
    QPushButton, # Neu für Buttons
    QWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("opTiSurf Browser")

        # --- Navigationsleiste erstellen ---
        navigation_bar = QHBoxLayout() # Horizontales Layout für Buttons und Adressleiste

        # Buttons erstellen
        self.back_button = QPushButton("←") # Oder "Zurück"
        self.forward_button = QPushButton("→") # Oder "Vorwärts"
        self.reload_button = QPushButton("↻") # Oder "Neu laden"
        self.stop_button = QPushButton("✕") # Oder "Stopp"

        # Button-Größe anpassen für einheitlicheres Aussehen (optional)
        # self.back_button.setFixedSize(30, 30)
        # self.forward_button.setFixedSize(30, 30)
        # self.reload_button.setFixedSize(30, 30)
        # self.stop_button.setFixedSize(30, 30)

        # Adressleiste erstellen
        self.address_bar = QLineEdit()

        # Buttons und Adressleiste zum Navigations-Layout hinzufügen
        navigation_bar.addWidget(self.back_button)
        navigation_bar.addWidget(self.forward_button)
        navigation_bar.addWidget(self.reload_button)
        navigation_bar.addWidget(self.stop_button)
        navigation_bar.addWidget(self.address_bar) # Adressleiste nimmt den Rest des Platzes

        # --- Web Engine View erstellen ---
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://example.com")) # Startseite

        # --- Signale verbinden ---
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_address_bar)

        # Button-Signale mit Browser-Aktionen verbinden
        self.back_button.clicked.connect(self.browser.back)
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button.clicked.connect(self.browser.reload)
        self.stop_button.clicked.connect(self.browser.stop)

        # (Optional, für später: Button-Status aktualisieren)
        # self.browser.history().canGoBackChanged.connect(self.back_button.setEnabled)
        # self.browser.history().canGoForwardChanged.connect(self.forward_button.setEnabled)


        # --- Hauptlayout erstellen (Vertikal) ---
        main_layout = QVBoxLayout()
        main_layout.addLayout(navigation_bar) # Navigationsleiste oben
        main_layout.addWidget(self.browser)   # Browser-Ansicht darunter

        # Abstände im Hauptlayout optimieren
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0) # Kein extra Abstand zwischen Navigationsleiste und Browser

        # Zentrales Widget erstellen und Layout setzen
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.resize(1024, 768)
        self.show()

    def navigate_to_url(self):
        url_text = self.address_bar.text()
        if not url_text.startswith("http://") and not url_text.startswith("https://"):
            url_text = "https://" + url_text
        self.browser.setUrl(QUrl(url_text))

    def update_address_bar(self, qurl):
        self.address_bar.setText(qurl.toString())
        self.address_bar.setCursorPosition(0)

# QApplication initialisieren
app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())