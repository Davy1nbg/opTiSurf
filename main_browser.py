import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.base_window_title = "opTiSurf Browser"
        self.setWindowTitle(self.base_window_title)

        navigation_bar = QHBoxLayout()

        self.back_button = QPushButton("←")
        self.forward_button = QPushButton("→")
        self.reload_button = QPushButton("↻")
        self.stop_button = QPushButton("✕")
        self.address_bar = QLineEdit()

        # Initialen Status der Navigationsbuttons setzen
        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)

        navigation_bar.addWidget(self.back_button)
        navigation_bar.addWidget(self.forward_button)
        navigation_bar.addWidget(self.reload_button)
        navigation_bar.addWidget(self.stop_button)
        navigation_bar.addWidget(self.address_bar)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://example.com"))

        # --- Signale verbinden ---
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_address_bar)
        self.browser.titleChanged.connect(self.update_window_title)
        
        # NEU: loadFinished Signal verbinden, um Button-Status zu aktualisieren
        self.browser.loadFinished.connect(self.update_navigation_button_states)

        self.back_button.clicked.connect(self.browser.back)
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button.clicked.connect(self.browser.reload)
        self.stop_button.clicked.connect(self.browser.stop)

        main_layout = QVBoxLayout()
        main_layout.addLayout(navigation_bar)
        main_layout.addWidget(self.browser)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

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

    def update_window_title(self, title):
        if title:
            self.setWindowTitle(f"{title} - {self.base_window_title}")
        else:
            self.setWindowTitle(self.base_window_title)

    # NEUE METHODE: Button-Status basierend auf Browser-History aktualisieren
    def update_navigation_button_states(self):
        history = self.browser.history()
        self.back_button.setEnabled(history.canGoBack())
        self.forward_button.setEnabled(history.canGoForward())

# QApplication initialisieren
app = QApplication(sys.argv)
window = MainWindow()
# Einmaliger Aufruf nach dem Erstellen des Fensters, um den initialen Status zu setzen,
# nachdem die erste Seite möglicherweise schon anfängt zu laden.
# loadFinished wird dies dann bei Bedarf korrigieren.
# Alternativ: Die erste Seite (example.com) wird geladen und löst loadFinished aus, was dann die Methode aufruft.
# window.update_navigation_button_states() # Kann hier auch aufgerufen werden, aber loadFinished sollte reichen.

sys.exit(app.exec())