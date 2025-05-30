from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QApplication, QLabel # QApplication für Clipboard
)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime # QDateTime für Timestamp-Formatierung
from PyQt6.QtGui import QGuiApplication # Für Clipboard

# from history_manager import HistoryManager # Nur für Type Hinting, Instanz wird übergeben

class HistoryDialog(QDialog):
    """
    Ein Dialog zur Anzeige und Verwaltung des Browserverlaufs.
    """
    # Signal, um eine URL im Hauptfenster zu öffnen (sauberere Alternative zum Attribut-Workaround)
    # open_url_requested = pyqtSignal(str) 

    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager # Referenz auf den HistoryManager

        self.setWindowTitle("Browserverlauf - opTiSurf")
        self.setMinimumSize(700, 500) # Etwas breiter für URL und Zeitstempel
        self.resize(800, 600)

        self._setup_ui()

        # Signal des HistoryManagers mit der populate-Methode verbinden
        self.history_manager.history_changed.connect(self.populate_history_tree)
        
        self.populate_history_tree() # Initial füllen

    def _setup_ui(self):
        """Erstellt die UI-Elemente des Dialogs."""
        main_layout = QVBoxLayout(self)

        # QTreeWidget für Verlaufseinträge
        self.history_tree_widget = QTreeWidget()
        self.history_tree_widget.setColumnCount(3) # Für Titel, URL, Zeit
        self.history_tree_widget.setHeaderLabels(["Titel", "URL", "Besuchszeit"])
        self.history_tree_widget.itemSelectionChanged.connect(self._update_button_states)
        self.history_tree_widget.itemDoubleClicked.connect(self._handle_item_double_clicked)
        main_layout.addWidget(self.history_tree_widget)

        # Button-Layout
        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Öffnen")
        self.open_button.setToolTip("Ausgewählten Verlaufseintrag im Browser öffnen.")
        self.open_button.clicked.connect(self._open_selected_item)
        button_layout.addWidget(self.open_button)

        self.copy_url_button = QPushButton("URL kopieren")
        self.copy_url_button.setToolTip("URL des ausgewählten Eintrags in die Zwischenablage kopieren.")
        self.copy_url_button.clicked.connect(self._copy_selected_url)
        button_layout.addWidget(self.copy_url_button)
        
        # Platzhalter für später: "Auswahl löschen"
        # self.delete_selected_button = QPushButton("Auswahl löschen")
        # self.delete_selected_button.clicked.connect(self._delete_selected_item)
        # button_layout.addWidget(self.delete_selected_button)

        button_layout.addStretch(1) # Flexibler Abstandhalter

        self.clear_all_button = QPushButton("Gesamten Verlauf löschen")
        self.clear_all_button.clicked.connect(self._clear_all_history_confirmed)
        button_layout.addWidget(self.clear_all_button)

        self.close_button = QPushButton("Schließen")
        self.close_button.clicked.connect(self.accept) # Schließt den Dialog
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)
        self._update_button_states() # Initialer Button-Status

    def populate_history_tree(self):
        """Leert den Baum und füllt ihn mit den aktuellen Verlaufseinträgen."""
        print("DEBUG [HistoryDialog]: populate_history_tree WIRD AUFGERUFEN")
        self.history_tree_widget.clear()
        self.history_tree_widget.setEnabled(True)

        # Hole Einträge, standardmäßig die neuesten zuerst (angenommen, das ist Standard in get_history_entries)
        history_entries = self.history_manager.get_history_entries(limit=200) # Lade z.B. die letzten 200 Einträge

        if not history_entries:
            no_history_item = QTreeWidgetItem(self.history_tree_widget, ["Kein Verlauf vorhanden."])
            no_history_item.setDisabled(True)
            self.history_tree_widget.setEnabled(False)
        else:
            for url, title, timestamp_str in history_entries:
                # Zeitstempel lesbar formatieren
                try:
                    dt_obj = QDateTime.fromString(timestamp_str, Qt.DateFormat.ISODateWithMs)
                    if not dt_obj.isValid(): # Fallback für ältere Timestamps ohne Millisekunden
                        dt_obj = QDateTime.fromString(timestamp_str, Qt.DateFormat.ISODate)
                    
                    # Lokale Zeitzone für die Anzeige verwenden
                    display_timestamp = dt_obj.toLocalTime().toString("dd.MM.yyyy hh:mm:ss")
                except Exception: # Breiter Fallback, falls das Parsen fehlschlägt
                    display_timestamp = timestamp_str 

                title_display = title if title else url # Wenn kein Titel, zeige URL
                
                tree_item = QTreeWidgetItem([title_display, url, display_timestamp])
                # Speichere die Originaldaten für Aktionen wie "Öffnen" oder "Löschen"
                tree_item.setData(0, Qt.ItemDataRole.UserRole, {"url": url, "title": title, "timestamp": timestamp_str})
                self.history_tree_widget.addTopLevelItem(tree_item)
            
            # Spaltenbreiten anpassen
            for i in range(self.history_tree_widget.columnCount()):
                self.history_tree_widget.resizeColumnToContents(i)
            self.history_tree_widget.setColumnWidth(1, 250) # URL-Spalte etwas breiter machen

        self._update_button_states()

    def _update_button_states(self):
        """Aktiviert oder deaktiviert Buttons basierend auf der Auswahl im Baum."""
        selected_items = self.history_tree_widget.selectedItems()
        is_item_selected = bool(selected_items)
        
        self.open_button.setEnabled(is_item_selected)
        self.copy_url_button.setEnabled(is_item_selected)
        # if hasattr(self, 'delete_selected_button'):
        #     self.delete_selected_button.setEnabled(is_item_selected)
        
        # Gesamten Verlauf löschen ist immer möglich, wenn Einträge da sind
        self.clear_all_button.setEnabled(self.history_tree_widget.topLevelItemCount() > 0 and 
                                          not (self.history_tree_widget.topLevelItemCount() == 1 and 
                                               self.history_tree_widget.topLevelItem(0).isDisabled()))


    def _open_selected_item(self):
        """Öffnet den ausgewählten Verlaufseintrag."""
        selected_items = self.history_tree_widget.selectedItems()
        if not selected_items:
            return
        
        item_data = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if item_data and item_data.get("url"):
            # Workaround für das Öffnen der URL durch die MainWindow:
            self.open_url_requested_via_double_click_or_button = item_data.get("url")
            self.accept() # Schließe den Dialog, damit MainWindow reagieren kann

    def _handle_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Behandelt einen Doppelklick auf ein Item im Baum (öffnet Verlaufseintrag)."""
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if item_data and item_data.get("url"):
            self.open_url_requested_via_double_click_or_button = item_data.get("url")
            self.accept()

    def _copy_selected_url(self):
        """Kopiert die URL des ausgewählten Eintrags in die Zwischenablage."""
        selected_items = self.history_tree_widget.selectedItems()
        if not selected_items:
            return
        
        item_data = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if item_data and item_data.get("url"):
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(item_data.get("url"))
            QMessageBox.information(self, "URL kopiert", "Die URL wurde in die Zwischenablage kopiert.")


    def _clear_all_history_confirmed(self):
        """Fragt nach Bestätigung und löscht dann den gesamten Verlauf."""
        reply = QMessageBox.question(self, 
                                     "Verlauf löschen", 
                                     "Möchten Sie wirklich den gesamten Browserverlauf unwiderruflich löschen?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.history_manager.clear_all_history():
                QMessageBox.information(self, "Verlauf gelöscht", "Der gesamte Browserverlauf wurde gelöscht.")
                # populate_history_tree wird durch das history_changed Signal des Managers aufgerufen
            else:
                QMessageBox.warning(self, "Fehler", "Der Verlauf konnte nicht gelöscht werden.")
    
    # Platzhalter für späteres Löschen einzelner Einträge
    # def _delete_selected_item(self):
    #     selected_items = self.history_tree_widget.selectedItems()
    #     if not selected_items: return
    #     item_data = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
    #     # Hier Logik zum Aufrufen einer Methode im HistoryManager, um spezifischen Eintrag zu löschen
    #     QMessageBox.information(self, "Info", "Löschen einzelner Einträge wird noch implementiert.")
    #     self._update_button_states()