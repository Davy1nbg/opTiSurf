from PyQt6.QtCore import QUrl, Qt, QSettings
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QMenu 
    # QMenuBar ist eine Methode von QMainWindow, QMenu wird für das Erstellen benötigt
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Importiere den Einstellungsdialog aus der anderen Datei
from settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.settings = QSettings("opTiSurfOrg", "opTiSurf") # Dieselben Namen verwenden

        self.base_window_title = "opTiSurf Browser"
        self.setWindowTitle(self.base_window_title)

        self._create_menu_bar()

        navigation_bar = QHBoxLayout()
        self.back_button = QPushButton("←")
        self.forward_button = QPushButton("→")
        self.reload_button = QPushButton("↻")
        self.stop_button = QPushButton("✕")
        self.address_bar = QLineEdit()

        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)

        navigation_bar.addWidget(self.back_button)
        navigation_bar.addWidget(self.forward_button)
        navigation_bar.addWidget(self.reload_button)
        navigation_bar.addWidget(self.stop_button)
        navigation_bar.addWidget(self.address_bar)

        self.browser = QWebEngineView()
        start_url = self.settings.value("startPageUrl", "https://example.com")
        self.browser.setUrl(QUrl(start_url))

        # Signale verbinden
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_address_bar)
        self.browser.titleChanged.connect(self.update_window_title)
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

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&Datei")

        settings_action = QAction("&Einstellungen...", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        file_menu.addAction(settings_action)

        exit_action = QAction("&Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            print("Einstellungen gespeichert. Die neue Startseite wird beim nächsten Start geladen oder wenn manuell neu geladen wird.")
        else:
            print("Einstellungen abgebrochen.")

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

    def update_navigation_button_states(self):
        history = self.browser.history()
        self.back_button.setEnabled(history.canGoBack())
        self.forward_button.setEnabled(history.canGoForward())