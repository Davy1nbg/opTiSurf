import json # Behalten, falls du es hier doch mal brauchst, sonst entfernen
import urllib.request # Behalten für UpdateCheckWorker, falls er hier definiert wäre
from packaging.version import parse as parse_version

from PyQt6.QtCore import QThread, QObject, pyqtSignal, QUrl, Qt, QSettings
from PyQt6.QtGui import QAction, QDesktopServices # QIcon ggf. hier importieren, wenn Icons verwendet werden
from PyQt6.QtWidgets import (
    QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QWidget, QMenu, QMessageBox, QInputDialog, QDialog
)
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile # Behalten für Browser-Interaktionen
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Eigene Modul-Imports
from update_checker import UpdateCheckWorker
from bookmark_manager import BookmarkManager
from settings_dialog import SettingsDialog
from bookmark_widgets import BookmarkManagerDialog, UNSORTED_FOLDER_NAME # UNSORTED_FOLDER_NAME importieren

# Globale Konstante für die Anwendung
CURRENT_APP_VERSION = "0.3.1" # Aktualisiere dies bei jedem Release

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._initialize_attributes()
        self._setup_ui_components()
        self._connect_signals()
        self._perform_initial_actions()

    def _initialize_attributes(self):
        """Initialisiert Kernattribute und Manager-Instanzen."""
        self.settings = QSettings("opTiSurfOrg", "opTiSurf")
        self.base_window_title = "opTiSurf Browser"
        self.setWindowTitle(self.base_window_title)

        self.bookmark_manager = BookmarkManager()
        self.browser = QWebEngineView()

    def _setup_ui_components(self):
        """Erstellt und arrangiert die Haupt-UI-Komponenten (Menü, Navigationsleiste, Layout)."""
        self._create_menu_bar()
        self._create_navigation_bar()
        self._setup_main_layout()

    def _connect_signals(self):
        """Verbindet alle notwendigen Signale der Anwendung mit den entsprechenden Slots."""
        if hasattr(self, 'bookmark_manager'): # Sicherstellen, dass bookmark_manager existiert
            self.bookmark_manager.bookmarks_changed.connect(self._update_bookmarks_menu)
        
        # Navigationsleisten-Signale
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.back_button.clicked.connect(self.browser.back)
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button.clicked.connect(self.browser.reload)
        self.stop_button.clicked.connect(self.browser.stop)

        # Browser-Signale
        self.browser.urlChanged.connect(self.update_address_bar)
        self.browser.titleChanged.connect(self.update_window_title)
        self.browser.loadFinished.connect(self.update_navigation_button_states)

    def _perform_initial_actions(self):
        """Führt Aktionen aus, die nach der UI-Initialisierung und dem Setzen von Signalen erfolgen."""
        start_url = self.settings.value("startPageUrl", "https://example.com")
        self.browser.setUrl(QUrl(start_url))
        
        self._update_bookmarks_menu() # Lesezeichen-Menü initial und korrekt füllen

        self.resize(1024, 768)
        self.show()

        # Update-Check beim Start (kann wieder aktiviert werden, wenn die Logik stabil ist)
        # self.perform_update_check(on_startup=True)

    def _create_menu_bar(self):
        """Erstellt die Menüleiste und die dazugehörigen Menüs und Aktionen."""
        menu_bar = self.menuBar()

        # Datei-Menü
        file_menu = menu_bar.addMenu("&Datei")
        settings_action = QAction("&Einstellungen...", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction("&Beenden", self)
        exit_action.triggered.connect(self.close) # self.close() ist eine Methode von QMainWindow
        file_menu.addAction(exit_action)

        # Lesezeichen-Menü
        # Das Menü selbst wird als Instanzattribut gespeichert, um es in _update_bookmarks_menu zu verwenden
        self.bookmarks_menu = menu_bar.addMenu("&Lesezeichen")
        
        # Statische Aktionen für das Lesezeichen-Menü als Instanzattribute definieren
        self.add_bookmark_action = QAction("Aktuelle Seite hinzufügen...", self)
        # self.add_bookmark_action.setIcon(QIcon("pfad/zum/add_icon.png")) # Beispiel für Icon-Pfad
        self.add_bookmark_action.triggered.connect(self._add_current_page_as_bookmark)

        self.manage_bookmarks_action = QAction("Lesezeichen verwalten...", self)
        # self.manage_bookmarks_action.setIcon(QIcon("pfad/zum/manage_icon.png")) # Beispiel
        self.manage_bookmarks_action.triggered.connect(self._open_bookmark_manager_dialog)
        
        # Das eigentliche Hinzufügen der Aktionen zum Menü erfolgt in _update_bookmarks_menu

        # Hilfe-Menü
        help_menu = menu_bar.addMenu("&Hilfe")
        check_for_updates_action = QAction("Nach Updates suchen...", self)
        check_for_updates_action.triggered.connect(lambda: self.perform_update_check(on_startup=False))
        help_menu.addAction(check_for_updates_action)

    def _create_navigation_bar(self):
        """Erstellt die UI-Elemente der Navigationsleiste und legt sie in einem Layout ab."""
        self.navigation_bar_layout = QHBoxLayout() # Layout als Instanzattribut speichern
        
        self.back_button = QPushButton("←")
        self.forward_button = QPushButton("→")
        self.reload_button = QPushButton("↻")
        self.stop_button = QPushButton("✕")
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("URL eingeben und Enter drücken...")

        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)

        self.navigation_bar_layout.addWidget(self.back_button)
        self.navigation_bar_layout.addWidget(self.forward_button)
        self.navigation_bar_layout.addWidget(self.reload_button)
        self.navigation_bar_layout.addWidget(self.stop_button)
        self.navigation_bar_layout.addWidget(self.address_bar)
        
    def _setup_main_layout(self):
        """Setzt das zentrale Widget und das Hauptlayout der Anwendung."""
        main_container_widget = QWidget() # Ein Container-Widget für das Hauptlayout
        main_layout = QVBoxLayout(main_container_widget) # Layout dem Container-Widget zuweisen

        if hasattr(self, 'navigation_bar_layout'): # Sicherstellen, dass das Layout existiert
            main_layout.addLayout(self.navigation_bar_layout)
        main_layout.addWidget(self.browser)
        
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.setCentralWidget(main_container_widget)

    def _add_current_page_as_bookmark(self):
        """Fügt die aktuell im Browser angezeigte Seite als Lesezeichen hinzu."""
        if not self.browser or not self.browser.url().isValid():
            QMessageBox.warning(self, "Lesezeichenfehler", "Keine gültige Seite zum Hinzufügen als Lesezeichen geladen.")
            return

        current_url = self.browser.url().toString()
        page_title = self.browser.page().title().strip()

        if not page_title: 
            page_title = current_url # Fallback, falls Seite keinen Titel hat

        if current_url == "about:blank":
            QMessageBox.warning(self, "Lesezeichenfehler", "Diese Seite kann nicht als Lesezeichen gespeichert werden.")
            return
        
        existing_folders = self.bookmark_manager.get_folder_names()
        folder_choices = [UNSORTED_FOLDER_NAME] + sorted(existing_folders) # UNSORTED_FOLDER_NAME importieren
        new_folder_option_text = "Neuen Ordner erstellen..."
        folder_choices.append(new_folder_option_text)

        chosen_folder_display_name, ok = QInputDialog.getItem(self, 
                                                      "Lesezeichen speichern in", 
                                                      "Ordner auswählen oder neuen Namen eingeben:", 
                                                      folder_choices, 
                                                      0, # Index von UNSORTED_FOLDER_NAME
                                                      True) # Editierbar machen

        if not ok or not chosen_folder_display_name:
            print("INFO: Hinzufügen des Lesezeichens abgebrochen.")
            return

        final_folder_name = None
        if chosen_folder_display_name == new_folder_option_text:
            new_custom_name, ok_new = QInputDialog.getText(self, "Neuer Ordner", "Name für neuen Ordner:")
            if ok_new and new_custom_name.strip():
                final_folder_name = new_custom_name.strip()
                # Stelle sicher, dass der Ordner im Manager bekannt wird, auch wenn er leer startet
                self.bookmark_manager.create_folder(final_folder_name) 
            else:
                print("INFO: Erstellung eines neuen Ordners abgebrochen oder leerer Name.")
                return
        elif chosen_folder_display_name != UNSORTED_FOLDER_NAME:
            final_folder_name = chosen_folder_display_name.strip()
        
        # Optional: Titel des Lesezeichens abfragen/bearbeiten lassen
        final_title, ok_title = QInputDialog.getText(self, "Lesezeichen Titel", "Titel für das Lesezeichen:", text=page_title)
        if not ok_title or not final_title.strip():
            print("INFO: Titelvergabe für Lesezeichen abgebrochen oder leerer Titel.")
            return
        page_title_to_save = final_title.strip()

        if self.bookmark_manager.add_bookmark(page_title_to_save, current_url, final_folder_name):
            QMessageBox.information(self, "Lesezeichen hinzugefügt", 
                                    f"Lesezeichen '{page_title_to_save}'\nwurde zu Ordner '{final_folder_name if final_folder_name else UNSORTED_FOLDER_NAME}' hinzugefügt.")
        # Das _update_bookmarks_menu wird durch das bookmarks_changed Signal vom BookmarkManager ausgelöst

    def _update_bookmarks_menu(self):
        """Aktualisiert das Lesezeichen-Menü dynamisch."""
        if not hasattr(self, 'bookmarks_menu'):
            print("WARNUNG: Lesezeichen-Menü nicht initialisiert für Update.")
            return

        self.bookmarks_menu.clear()

        # Statische Aktionen (definiert in _create_menu_bar) wieder hinzufügen
        if hasattr(self, 'add_bookmark_action'):
            self.bookmarks_menu.addAction(self.add_bookmark_action)
        if hasattr(self, 'manage_bookmarks_action'):
            self.bookmarks_menu.addAction(self.manage_bookmarks_action)
        
        self.bookmarks_menu.addSeparator()

        bookmarks_list = self.bookmark_manager.get_all_bookmarks()
        # Hier könnte man später eine komplexere Logik einbauen, um Ordner als Untermenüs darzustellen.
        # Fürs Erste: Flache Liste aller Lesezeichen.
        if bookmarks_list:
            for bm in reversed(bookmarks_list): # Neueste Lesezeichen zuerst
                # Nur Lesezeichen mit Titel und URL anzeigen
                if bm.get('title') and bm.get('url'): 
                    display_text = bm['title']
                    if bm.get('folder_name'): # Optional Ordnernamen im Menü anzeigen
                        display_text += f" ({bm['folder_name']})"
                    
                    action = QAction(display_text, self)
                    action.setData(bm) # Speichere das ganze Lesezeichen-Dictionary
                    action.setToolTip(bm['url']) # Zeige URL als Tooltip
                    action.triggered.connect(self._open_bookmark_from_menu)
                    self.bookmarks_menu.addAction(action)
        else:
            no_bookmarks_action = QAction("Keine Lesezeichen vorhanden", self)
            no_bookmarks_action.setEnabled(False)
            self.bookmarks_menu.addAction(no_bookmarks_action)

    def _open_bookmark_from_menu(self):
        """Öffnet ein Lesezeichen, das aus dem Menü ausgewählt wurde."""
        action = self.sender() 
        if action and isinstance(action, QAction):
            bookmark_data = action.data() # Sollte das Lesezeichen-Dictionary sein
            if isinstance(bookmark_data, dict) and bookmark_data.get('url'):
                url_to_load = bookmark_data['url']
                self.browser.setUrl(QUrl(url_to_load))
            # Der Fall, dass nur ein String als data gespeichert wurde, ist hier nicht mehr relevant,
            # da wir das ganze Dictionary speichern.

    def _open_bookmark_manager_dialog(self):
        """Öffnet den Dialog zur Verwaltung der Lesezeichen."""
        if not hasattr(self, 'bookmark_manager'):
            QMessageBox.critical(self, "Fehler", "Lesezeichen-Manager nicht initialisiert.")
            return
        
        dialog = BookmarkManagerDialog(self.bookmark_manager, self)
        
        # Workaround für Doppelklick im Dialog (Signal wäre sauberer)
        if hasattr(dialog, 'double_clicked_bookmark_url'):
            del dialog.double_clicked_bookmark_url 

        dialog.exec() # Modaler Dialog

        if hasattr(dialog, 'double_clicked_bookmark_url') and dialog.double_clicked_bookmark_url:
            url_to_load = dialog.double_clicked_bookmark_url
            print(f"INFO: Lade Lesezeichen via Doppelklick aus Dialog: {url_to_load}")
            self.browser.setUrl(QUrl(url_to_load))
        # Änderungen im Dialog sollten das bookmarks_changed Signal auslösen und das Menü aktualisieren.

    def perform_update_check(self, on_startup=False):
        """Startet den asynchronen Prozess zur Überprüfung auf Anwendungsupdates."""
        self.update_check_on_startup = on_startup 
        self.update_thread = QThread()
        self.update_worker = UpdateCheckWorker(CURRENT_APP_VERSION) # Nutzt globale App-Version
        self.update_worker.moveToThread(self.update_thread)

        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished.connect(self.handle_update_check_result)
        
        # Sicherstellen, dass Worker und Thread nach Beendigung aufgeräumt werden
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)

        self.update_thread.start()
        if not on_startup:
            print("INFO: Suche nach Updates...")

    def handle_update_check_result(self, result: dict):
        """Verarbeitet das Ergebnis der Update-Prüfung."""
        if result.get("error"):
            if not self.update_check_on_startup: 
                QMessageBox.warning(self, "Update-Fehler", 
                                    f"Fehler beim Suchen nach Updates:\n{result['error']}")
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
        elif not self.update_check_on_startup: # Nur bei manuellem Check "Kein Update" anzeigen
            QMessageBox.information(self, "Keine Updates", 
                                    f"Sie verwenden die aktuellste Version von opTiSurf ({CURRENT_APP_VERSION}).")
    
    def open_settings_dialog(self):
        """Öffnet den Einstellungsdialog."""
        dialog = SettingsDialog(self)
        if dialog.exec(): # True wenn OK geklickt wurde
            print("INFO: Einstellungen gespeichert.")
            # Cookie-spezifische Logik wurde entfernt.
            QMessageBox.information(self, 
                                    "Einstellungen übernommen", 
                                    "Änderungen an der Startseite werden beim nächsten Start des Browsers wirksam.")
        else:
            print("INFO: Einstellungen abgebrochen.")

    def navigate_to_url(self):
        """Navigiert zur URL, die in der Adressleiste eingegeben wurde."""
        url_text = self.address_bar.text().strip()
        if not url_text:
            return
        if not (url_text.startswith("http://") or url_text.startswith("https://")):
            url_text = "https://" + url_text
        self.browser.setUrl(QUrl(url_text))

    def update_address_bar(self, qurl: QUrl):
        """Aktualisiert die Adressleiste mit der aktuellen URL."""
        self.address_bar.setText(qurl.toString())
        self.address_bar.setCursorPosition(0)

    def update_window_title(self, title: str):
        """Aktualisiert den Fenstertitel."""
        if title:
            self.setWindowTitle(f"{title.strip()} - {self.base_window_title}")
        else:
            self.setWindowTitle(self.base_window_title)

    def update_navigation_button_states(self):
        """Aktualisiert den Aktivierungsstatus der Navigationsbuttons."""
        if hasattr(self, 'browser') and self.browser and self.browser.page() and self.browser.page().history():
            history = self.browser.page().history()
            self.back_button.setEnabled(history.canGoBack())
            self.forward_button.setEnabled(history.canGoForward())
        else:
            # Fallback, falls Browser oder History nicht verfügbar
            self.back_button.setEnabled(False)
            self.forward_button.setEnabled(False)