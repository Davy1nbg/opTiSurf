import json
import urllib.request
from packaging.version import parse as parse_version # Robusterer Versionsvergleich
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QUrl
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QDesktopServices
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

# main_window.py
CURRENT_APP_VERSION = "0.3.0" # Beispiel: Setze hier deine aktuelle Version ein!
GITHUB_REPO_OWNER = "davy1nbg" # Dein GitHub Benutzername
GITHUB_REPO_NAME = "opTiSurf" # Name deines Repos (oder wie es heißt)

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

        # Update-Check beim Start durchführen
        self.perform_update_check(on_startup=True)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&Datei")

        settings_action = QAction("&Einstellungen...", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        file_menu.addAction(settings_action)
        file_menu.addSeparator() # Trennlinie
        exit_action = QAction("&Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # NEU: Hilfe-Menü für Update-Check
        help_menu = menu_bar.addMenu("&Hilfe")
        check_for_updates_action = QAction("Nach Updates suchen...", self)
        check_for_updates_action.triggered.connect(lambda: self.perform_update_check(on_startup=False))
        help_menu.addAction(check_for_updates_action)

    def perform_update_check(self, on_startup=False):
        self.update_check_on_startup = on_startup # Speichern für den Handler

        self.update_thread = QThread()
        self.update_worker = UpdateCheckWorker(CURRENT_APP_VERSION, GITHUB_REPO_OWNER, GITHUB_REPO_NAME)
        self.update_worker.moveToThread(self.update_thread)

        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished.connect(self.handle_update_check_result)
        
        # Aufräumen nach Beendigung
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)

        self.update_thread.start()
        if not on_startup:
            print("Suche nach Updates...")


    def handle_update_check_result(self, result):
        print(f"Update-Check Ergebnis: {result}") # Für Debugging
        if result.get("error"):
            if not self.update_check_on_startup: # Nur Fehler anzeigen, wenn manuell ausgelöst
                QMessageBox.warning(self, "Update-Fehler", f"Fehler beim Suchen nach Updates:\n{result['error']}")
            return

        if result.get("update_available"):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Update verfügbar!")
            msg_box.setText(f"Eine neue Version von opTiSurf ({result['latest_version']}) ist verfügbar.\n"
                            f"Sie verwenden Version {CURRENT_APP_VERSION}.\n\n"
                            "Möchten Sie die Download-Seite jetzt öffnen?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl(result['html_url']))
        else:
            if not self.update_check_on_startup: # Nur anzeigen, wenn manuell ausgelöst
                QMessageBox.information(self, "Keine Updates", f"Sie verwenden die aktuellste Version von opTiSurf ({CURRENT_APP_VERSION}).")
        
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

class UpdateCheckWorker(QObject):
    finished = pyqtSignal(dict) # Signal sendet ein Dictionary mit Ergebnissen

    def __init__(self, current_version_str, owner, repo):
        super().__init__()
        self.current_version_str = current_version_str
        self.owner = owner
        self.repo = repo

    def run(self):
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        result = {
            "update_available": False,
            "latest_version": self.current_version_str,
            "html_url": "",
            "error": None
        }

        try:
            with urllib.request.urlopen(api_url, timeout=10) as response:
                if response.status == 200:
                    data = json.load(response)
                    latest_version_str = data.get("tag_name", "").lstrip('v') # 'v0.4.0' -> '0.4.0'
                    html_url = data.get("html_url", "")

                    if not latest_version_str:
                        result["error"] = "Kein tag_name im Release gefunden."
                        self.finished.emit(result)
                        return

                    result["latest_version"] = latest_version_str
                    result["html_url"] = html_url
                    
                    current_v = parse_version(self.current_version_str)
                    latest_v = parse_version(latest_version_str)

                    if latest_v > current_v:
                        result["update_available"] = True
                else:
                    result["error"] = f"Fehler bei API-Abfrage: Status {response.status}"
        except urllib.error.URLError as e:
            result["error"] = f"Netzwerkfehler: {e.reason}"
        except json.JSONDecodeError:
            result["error"] = "Fehler beim Parsen der API-Antwort."
        except Exception as e:
            result["error"] = f"Unbekannter Fehler: {str(e)}"
        
        self.finished.emit(result)