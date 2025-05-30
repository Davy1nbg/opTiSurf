import json # Wird aktuell nicht direkt in dieser Datei verwendet
import urllib.request # Wird aktuell nicht direkt in dieser Datei verwendet
from packaging.version import parse as parse_version # Wird aktuell nicht direkt hier verwendet

from PyQt6.QtCore import QThread, QObject, pyqtSignal, QUrl, Qt, QSettings
from PyQt6.QtGui import QAction, QDesktopServices # QIcon ggf. importieren, wenn du Icons für Aktionen setzt
from PyQt6.QtWidgets import (
    QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QWidget, QMenu, QMessageBox, QInputDialog, QDialog
)
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile # Bleibt für Browser-Funktionen
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Eigene Modul-Imports
from update_checker import UpdateCheckWorker
from bookmark_manager import BookmarkManager
from settings_dialog import SettingsDialog
from bookmark_widgets import BookmarkManagerDialog, UNSORTED_FOLDER_NAME
from history_manager import HistoryManager
from history_widgets import HistoryDialog # Annahme: HistoryDialog ist hier definiert oder wird importiert
from config import (
    START_PAGE_SETTING_KEY, DEFAULT_START_PAGE,
    HISTORY_DURATION_SETTING_KEY, HISTORY_DURATION_OPTIONS, DEFAULT_HISTORY_DURATION_DAYS
)

# Globale Konstante für die Anwendung
CURRENT_APP_VERSION = "0.4.0" # Beispiel: Aktualisiere dies bei jedem Release

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
        self.history_manager = HistoryManager()
        self.browser = QWebEngineView()

    def _setup_ui_components(self):
        """Erstellt und arrangiert die Haupt-UI-Komponenten."""
        self._create_menu_bar()
        self._create_navigation_bar()
        self._setup_main_layout()

    def _connect_signals(self):
        """Verbindet alle notwendigen Signale mit Slots."""
        if hasattr(self, 'bookmark_manager'):
            self.bookmark_manager.bookmarks_changed.connect(self._update_bookmarks_menu)
        if hasattr(self, 'history_manager'): # Signal für History-Dialog
             self.history_manager.history_changed.connect(self._handle_history_changed_for_dialogs)

        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.back_button.clicked.connect(self.browser.back)
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button.clicked.connect(self.browser.reload)
        self.stop_button.clicked.connect(self.browser.stop)

        self.browser.urlChanged.connect(self.update_address_bar)
        self.browser.titleChanged.connect(self.update_window_title)
        self.browser.loadFinished.connect(self.update_navigation_button_states)
        self.browser.loadFinished.connect(self._add_to_history)

    def _perform_initial_actions(self):
        """Führt Aktionen aus, die nach der UI-Initialisierung erfolgen."""
        start_url = self.settings.value(START_PAGE_SETTING_KEY, DEFAULT_START_PAGE)
        self.browser.setUrl(QUrl(start_url))
        
        if hasattr(self, 'history_manager'):
            days_to_keep = self.settings.value(HISTORY_DURATION_SETTING_KEY, 
                                               DEFAULT_HISTORY_DURATION_DAYS,
                                               type=int) 
            # print(f"INFO [MainWindow]: Rufe Verlaufsbereinigung auf (Einstellung: {days_to_keep} Tage).") # Kann für Release reduziert werden
            self.history_manager.cleanup_old_history_entries(days_to_keep)
        
        self._update_bookmarks_menu()

        self.resize(1024, 768)
        self.show()

        # self.perform_update_check(on_startup=True) # Update-Check kann hier aktiviert werden

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
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Lesezeichen-Menü
        self.bookmarks_menu = menu_bar.addMenu("&Lesezeichen")
        self.add_bookmark_action = QAction("Aktuelle Seite hinzufügen...", self)
        self.add_bookmark_action.triggered.connect(self._add_current_page_as_bookmark)
        self.manage_bookmarks_action = QAction("Lesezeichen verwalten...", self)
        self.manage_bookmarks_action.triggered.connect(self._open_bookmark_manager_dialog)
        # Die Aktionen werden durch _update_bookmarks_menu() dem Menü hinzugefügt

        # Verlauf-Menü
        self.history_menu = menu_bar.addMenu("&Verlauf") # Als Instanzattribut speichern für ggf. dyn. Einträge
        show_history_action = QAction("Gesamten Verlauf anzeigen...", self)
        show_history_action.triggered.connect(self._open_history_dialog)
        self.history_menu.addAction(show_history_action)
        # Hier könnten später die letzten X Verlaufseinträge dynamisch hinzugefügt werden

        # Hilfe-Menü
        help_menu = menu_bar.addMenu("&Hilfe")
        check_for_updates_action = QAction("Nach Updates suchen...", self)
        check_for_updates_action.triggered.connect(lambda: self.perform_update_check(on_startup=False))
        help_menu.addAction(check_for_updates_action)

    def _create_navigation_bar(self):
        """Erstellt die UI-Elemente der Navigationsleiste."""
        self.navigation_bar_layout = QHBoxLayout()
        
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
        main_container_widget = QWidget() 
        main_layout = QVBoxLayout(main_container_widget)

        if hasattr(self, 'navigation_bar_layout'):
            main_layout.addLayout(self.navigation_bar_layout)
        main_layout.addWidget(self.browser)
        
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.setCentralWidget(main_container_widget)

    def _add_to_history(self, ok: bool):
        """Fügt die aktuell geladene Seite zum Verlauf hinzu, wenn das Laden erfolgreich war."""
        if ok and hasattr(self, 'history_manager') and self.browser and self.browser.url().isValid():
            url = self.browser.url().toString()
            title = self.browser.page().title()
            if url != "about:blank": # Ignoriere "about:blank" für den Verlauf
                self.history_manager.add_visit(url, title)

    def _add_current_page_as_bookmark(self):
        """Fügt die aktuell im Browser angezeigte Seite als Lesezeichen hinzu."""
        if not self.browser or not self.browser.url().isValid():
            QMessageBox.warning(self, "Lesezeichenfehler", "Keine gültige Seite zum Hinzufügen als Lesezeichen geladen.")
            return

        current_url = self.browser.url().toString()
        page_title = self.browser.page().title().strip()

        if not page_title: 
            page_title = current_url

        if current_url == "about:blank":
            QMessageBox.warning(self, "Lesezeichenfehler", "Diese Seite kann nicht als Lesezeichen gespeichert werden.")
            return
        
        existing_folders = self.bookmark_manager.get_folder_names()
        folder_choices = [UNSORTED_FOLDER_NAME] + sorted(existing_folders)
        new_folder_option_text = "Neuen Ordner erstellen..."
        folder_choices.append(new_folder_option_text)

        chosen_folder_display_name, ok = QInputDialog.getItem(self, 
                                                      "Lesezeichen speichern in", 
                                                      "Ordner auswählen oder neuen Namen eingeben:", 
                                                      folder_choices, 0, True)

        if not ok or not chosen_folder_display_name:
            # print("INFO: Hinzufügen des Lesezeichens abgebrochen.") # Für Debugging
            return

        final_folder_name = None
        if chosen_folder_display_name == new_folder_option_text:
            new_custom_name, ok_new = QInputDialog.getText(self, "Neuer Ordner", "Name für neuen Ordner:")
            if ok_new and new_custom_name.strip():
                final_folder_name = new_custom_name.strip()
                self.bookmark_manager.create_folder(final_folder_name) 
            else:
                return
        elif chosen_folder_display_name != UNSORTED_FOLDER_NAME:
            final_folder_name = chosen_folder_display_name.strip()
        
        final_title, ok_title = QInputDialog.getText(self, "Lesezeichen Titel", "Titel für das Lesezeichen:", text=page_title)
        if not ok_title or not final_title.strip():
            return
        page_title_to_save = final_title.strip()

        if self.bookmark_manager.add_bookmark(page_title_to_save, current_url, final_folder_name):
            QMessageBox.information(self, "Lesezeichen hinzugefügt", 
                                    f"Lesezeichen '{page_title_to_save}'\nwurde zu Ordner '{final_folder_name if final_folder_name else UNSORTED_FOLDER_NAME}' hinzugefügt.")
        # _update_bookmarks_menu wird durch das bookmarks_changed Signal vom BookmarkManager ausgelöst

    def _update_bookmarks_menu(self):
        """Aktualisiert das Lesezeichen-Menü dynamisch."""
        if not hasattr(self, 'bookmarks_menu'):
            return

        self.bookmarks_menu.clear()

        if hasattr(self, 'add_bookmark_action'):
            self.bookmarks_menu.addAction(self.add_bookmark_action)
        if hasattr(self, 'manage_bookmarks_action'):
            self.bookmarks_menu.addAction(self.manage_bookmarks_action)
        
        self.bookmarks_menu.addSeparator()

        bookmarks_list = self.bookmark_manager.get_all_bookmarks()
        if bookmarks_list:
            for bm in reversed(bookmarks_list): 
                if bm.get('title') and bm.get('url'): 
                    display_text = bm['title']
                    if bm.get('folder_name'):
                        display_text += f" ({bm['folder_name']})"
                    
                    action = QAction(display_text, self)
                    action.setData(bm) 
                    action.setToolTip(bm['url'])
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
            bookmark_data = action.data()
            if isinstance(bookmark_data, dict) and bookmark_data.get('url'):
                url_to_load = bookmark_data['url']
                self.browser.setUrl(QUrl(url_to_load))

    def _open_bookmark_manager_dialog(self):
        """Öffnet den Dialog zur Verwaltung der Lesezeichen."""
        if not hasattr(self, 'bookmark_manager'):
            QMessageBox.critical(self, "Fehler", "Lesezeichen-Manager nicht initialisiert.")
            return
        
        dialog = BookmarkManagerDialog(self.bookmark_manager, self)
        
        if hasattr(dialog, 'double_clicked_bookmark_url'): # Workaround für Doppelklick
            del dialog.double_clicked_bookmark_url 

        dialog.exec()

        if hasattr(dialog, 'double_clicked_bookmark_url') and dialog.double_clicked_bookmark_url:
            url_to_load = dialog.double_clicked_bookmark_url
            self.browser.setUrl(QUrl(url_to_load))

    def _open_history_dialog(self):
        """Öffnet den Dialog zur Anzeige des Browserverlaufs."""
        if not hasattr(self, 'history_manager'):
            QMessageBox.critical(self, "Fehler", "Verlaufs-Manager nicht initialisiert.")
            return
        
        dialog = HistoryDialog(self.history_manager, self)
        
        if hasattr(dialog, 'open_url_requested_via_double_click_or_button'): # Workaround für Doppelklick/Öffnen
            del dialog.open_url_requested_via_double_click_or_button

        dialog.exec()

        if hasattr(dialog, 'open_url_requested_via_double_click_or_button') and \
           dialog.open_url_requested_via_double_click_or_button:
            url_to_load = dialog.open_url_requested_via_double_click_or_button
            self.browser.setUrl(QUrl(url_to_load))
            
    def _handle_history_changed_for_dialogs(self):
        """Slot, der aufgerufen wird, wenn sich der Verlauf ändert.
           Könnte verwendet werden, um geöffnete Verlaufsdialoge zu aktualisieren.
           Momentan verlässt sich HistoryDialog auf sein eigenes Signal-Connect beim Init.
        """
        # print("DEBUG [MainWindow]: History changed signal received.")
        # Wenn der HistoryDialog ein update_content() hätte und wir eine Referenz darauf:
        # if hasattr(self, 'current_history_dialog') and self.current_history_dialog.isVisible():
        # self.current_history_dialog.populate_history_tree() # Beispiel
        pass


    def perform_update_check(self, on_startup=False):
        """Startet den asynchronen Prozess zur Überprüfung auf Anwendungsupdates."""
        self.update_check_on_startup = on_startup 
        self.update_thread = QThread()
        self.update_worker = UpdateCheckWorker(CURRENT_APP_VERSION)
        self.update_worker.moveToThread(self.update_thread)

        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished.connect(self.handle_update_check_result)
        
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
        elif not self.update_check_on_startup:
            QMessageBox.information(self, "Keine Updates", 
                                    f"Sie verwenden die aktuellste Version von opTiSurf ({CURRENT_APP_VERSION}).")
    
    def open_settings_dialog(self):
        """Öffnet den Einstellungsdialog und gibt eine spezifische Rückmeldung zu Änderungen."""
        old_start_page = self.settings.value(START_PAGE_SETTING_KEY, DEFAULT_START_PAGE)
        old_history_duration = self.settings.value(HISTORY_DURATION_SETTING_KEY, 
                                                   DEFAULT_HISTORY_DURATION_DAYS, type=int)

        dialog = SettingsDialog(self)
        
        if dialog.exec():
            new_start_page = self.settings.value(START_PAGE_SETTING_KEY, DEFAULT_START_PAGE)
            new_history_duration = self.settings.value(HISTORY_DURATION_SETTING_KEY, 
                                                       DEFAULT_HISTORY_DURATION_DAYS, type=int)
            changed_messages = []
            settings_were_changed = False

            if old_start_page != new_start_page:
                changed_messages.append("Die **Startseite** wird beim nächsten Start des Browsers geändert.")
                settings_were_changed = True
            
            if old_history_duration != new_history_duration:
                duration_text = "unbekannt"
                for text, days in HISTORY_DURATION_OPTIONS.items(): 
                    if days == new_history_duration:
                        duration_text = text.lower().replace(" (standard)", "")
                        break
                changed_messages.append(f"Die **Speicherdauer des Verlaufs** wurde auf '{duration_text}' geändert und wird beim nächsten Start für die Bereinigung angewendet.")
                settings_were_changed = True
            
            if settings_were_changed:
                final_message_title = "Einstellungen erfolgreich geändert"
                final_message_text = "Folgende Einstellungen wurden angepasst:\n\n- " + "\n- ".join(changed_messages)
            else:
                final_message_title = "Einstellungen gespeichert"
                final_message_text = "Es wurden keine Änderungen an den Einstellungen vorgenommen."
            QMessageBox.information(self, final_message_title, final_message_text)
        else:
            print("INFO: Einstellungsdialog abgebrochen.")

    def navigate_to_url(self):
        """Navigiert zur URL aus der Adressleiste."""
        url_text = self.address_bar.text().strip()
        if not url_text: return
        if not (url_text.startswith("http://") or url_text.startswith("https://")):
            url_text = "https://" + url_text
        self.browser.setUrl(QUrl(url_text))

    def update_address_bar(self, qurl: QUrl):
        """Aktualisiert die Adressleiste mit der aktuellen URL."""
        self.address_bar.setText(qurl.toString())
        self.address_bar.setCursorPosition(0)

    def update_window_title(self, title: str):
        """Aktualisiert den Fenstertitel mit dem Titel der aktuellen Seite."""
        page_title = title.strip() if title else ""
        if page_title:
            self.setWindowTitle(f"{page_title} - {self.base_window_title}")
        else:
            self.setWindowTitle(self.base_window_title)

    def update_navigation_button_states(self):
        """Aktualisiert den Aktivierungsstatus der Vorwärts-/Rückwärts-Buttons."""
        if hasattr(self, 'browser') and self.browser and self.browser.page() and self.browser.page().history():
            history = self.browser.page().history()
            self.back_button.setEnabled(history.canGoBack())
            self.forward_button.setEnabled(history.canGoForward())
        else:
            self.back_button.setEnabled(False)
            self.forward_button.setEnabled(False)