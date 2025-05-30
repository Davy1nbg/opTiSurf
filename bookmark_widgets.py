from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
# pyqtSignal wird hier nicht direkt vom Dialog gesendet, aber es ist kein Fehler, es importiert zu lassen.
# from PyQt6.QtGui import QIcon # Importieren, wenn du Icons für Ordner/Lesezeichen setzen willst

# Konstante für den "Ordner" der unsortierten Lesezeichen
UNSORTED_FOLDER_NAME = "Unsortiert" # Wird auch in MainWindow verwendet, ggf. zentral definieren

class BookmarkManagerDialog(QDialog):
    """
    Dialog zur Verwaltung von Lesezeichen: Anzeigen in Ordnerstruktur,
    Hinzufügen neuer Ordner (logisch) und Löschen von Lesezeichen/leeren Ordnern.
    """
    # Wenn der Dialog komplexere Aktionen auslöst, die MainWindow direkt betreffen sollen,
    # könnten hier Signale definiert werden, z.B. für "bookmark_selected_for_opening"
    # bookmark_double_clicked_url = pyqtSignal(str) # Beispiel für ein besseres Signal

    def __init__(self, bookmark_manager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager # Referenz auf den BookmarkManager

        self.setWindowTitle("Lesezeichen-Manager - opTiSurf")
        self.setMinimumSize(500, 300) # Mindestgröße etwas reduziert, kann angepasst werden
        self.resize(600, 450)

        self._setup_ui()
        self.bookmark_manager.bookmarks_changed.connect(self.populate_bookmarks_tree)
        self.populate_bookmarks_tree()

    def _setup_ui(self):
        """Erstellt die UI-Elemente des Dialogs."""
        main_layout = QVBoxLayout(self)

        self.bookmarks_tree_widget = QTreeWidget()
        self.bookmarks_tree_widget.setHeaderHidden(True)
        self.bookmarks_tree_widget.itemSelectionChanged.connect(self._update_button_states)
        self.bookmarks_tree_widget.itemDoubleClicked.connect(self._handle_item_double_clicked)
        main_layout.addWidget(self.bookmarks_tree_widget)

        button_layout = QHBoxLayout()
        
        self.add_folder_button = QPushButton("Neuer Ordner...")
        self.add_folder_button.setToolTip("Erstellt einen neuen Ordnernamen (wird sichtbar, wenn Lesezeichen hinzugefügt werden).")
        self.add_folder_button.clicked.connect(self.add_new_folder_interactive)
        button_layout.addWidget(self.add_folder_button)

        self.delete_button = QPushButton("Auswahl löschen")
        self.delete_button.setEnabled(False) # Initial deaktiviert
        self.delete_button.clicked.connect(self.delete_selected_item)
        button_layout.addWidget(self.delete_button)
        
        # Hier könnte ein "Bearbeiten"-Button hin
        # self.edit_button = QPushButton("Bearbeiten...")
        # self.edit_button.setEnabled(False)
        # self.edit_button.clicked.connect(self.edit_selected_item)
        # button_layout.addWidget(self.edit_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Schließen")
        self.close_button.clicked.connect(self.accept) # Standardverhalten für "OK" oder Schließen
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    def populate_bookmarks_tree(self):
        """Leert den Baum und füllt ihn mit Ordnern und Lesezeichen aus dem BookmarkManager."""
        self.bookmarks_tree_widget.clear()
        self.bookmarks_tree_widget.setEnabled(True) # Standardmäßig aktiviert

        folder_names = self.bookmark_manager.get_folder_names()
        # Um eine konsistente Reihenfolge zu haben (z.B. "Unsortiert" immer unten oder oben),
        # könnte man hier noch sortieren oder die Logik anpassen.
        
        created_folder_items = {} # Speichert QTreeWidgetItems für Ordner per Namen

        # 1. Explizite/Genutzte Ordner erstellen
        for folder_name in folder_names:
            folder_item = QTreeWidgetItem(self.bookmarks_tree_widget, [folder_name])
            folder_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "folder", "name": folder_name})
            # folder_item.setIcon(0, QIcon("icons/folder.png")) # Beispiel für Icon
            created_folder_items[folder_name] = folder_item

            bookmarks_in_folder = self.bookmark_manager.get_bookmarks_by_folder_name(folder_name)
            for bm in bookmarks_in_folder:
                title = bm.get('title', 'Unbenannt')
                bookmark_item = QTreeWidgetItem(folder_item, [title])
                bookmark_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "bookmark", "id": bm.get('id'), 
                    "url": bm.get('url'), "title": title
                })
                # bookmark_item.setIcon(0, QIcon("icons/bookmark.png")) # Beispiel

        # 2. Unsortierte Lesezeichen hinzufügen
        unsorted_bookmarks = self.bookmark_manager.get_bookmarks_by_folder_name(None)
        if unsorted_bookmarks:
            unsorted_folder_item = QTreeWidgetItem(self.bookmarks_tree_widget, [UNSORTED_FOLDER_NAME])
            unsorted_folder_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "folder_unsorted", "name": None})
            # unsorted_folder_item.setIcon(0, QIcon("icons/unsorted_folder.png")) # Beispiel
            for bm in unsorted_bookmarks:
                title = bm.get('title', 'Unbenannt')
                bookmark_item = QTreeWidgetItem(unsorted_folder_item, [title])
                bookmark_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "bookmark", "id": bm.get('id'),
                    "url": bm.get('url'), "title": title
                })
        
        if not folder_names and not unsorted_bookmarks:
            # self.bookmarks_tree_widget.addItem(QListWidgetItem("Keine Lesezeichen vorhanden.")) # War falsch
            no_bm_item = QTreeWidgetItem(self.bookmarks_tree_widget, ["Keine Lesezeichen vorhanden."])
            no_bm_item.setDisabled(True) # Item ausgrauen
            self.bookmarks_tree_widget.setEnabled(False) # Ganze Liste deaktivieren ist vielleicht zu viel

        self.bookmarks_tree_widget.expandAll() # Alle Ordner ausklappen
        self._update_button_states()

    def _update_button_states(self):
        """Aktualisiert den Zustand der Buttons basierend auf der Auswahl im Baum."""
        selected_items = self.bookmarks_tree_widget.selectedItems()
        is_item_selected = bool(selected_items)
        
        self.delete_button.setEnabled(is_item_selected)
        # if hasattr(self, 'edit_button'):
        #     self.edit_button.setEnabled(is_item_selected)

    def add_new_folder_interactive(self):
        """Fragt den Nutzer nach einem Namen für einen neuen Ordner und erstellt diesen im BookmarkManager."""
        folder_name, ok = QInputDialog.getText(self, "Neuer Ordner", "Name des neuen Ordners:")
        if ok and folder_name.strip():
            clean_folder_name = folder_name.strip()
            if clean_folder_name == UNSORTED_FOLDER_NAME: # Reservierten Namen nicht erlauben
                QMessageBox.warning(self, "Ungültiger Name", f"Der Ordnername '{UNSORTED_FOLDER_NAME}' ist reserviert.")
                return

            if self.bookmark_manager.create_folder(clean_folder_name): # create_folder sollte True bei Erfolg zurückgeben
                QMessageBox.information(self, "Ordner erstellt", f"Der Ordner '{clean_folder_name}' wurde erstellt.")
                # populate_bookmarks_tree wird durch das bookmarks_changed Signal des Managers aufgerufen,
                # wenn create_folder dieses Signal aussendet (was es in unserer Version tut).
            else:
                # Entweder existierte der Ordner schon oder der Name war ungültig (BookmarkManager sollte das loggen)
                 QMessageBox.warning(self, "Ordner nicht erstellt", f"Der Ordner '{clean_folder_name}' konnte nicht erstellt werden oder existiert bereits.")
        else:
            print("INFO: Erstellung eines neuen Ordners abgebrochen oder leerer Name.")

    def _handle_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Behandelt einen Doppelklick auf ein Item im Baum (öffnet Lesezeichen)."""
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if item_data and item_data.get("type") == "bookmark":
            url_to_open = item_data.get("url")
            if url_to_open:
                # Workaround für das Öffnen der URL durch die MainWindow:
                # Setze ein Attribut, das MainWindow nach dialog.exec() prüfen kann.
                # Eine Signal-Slot-Verbindung vom Dialog zur MainWindow wäre sauberer.
                self.double_clicked_bookmark_url = url_to_open 
                self.accept() # Schließe den Dialog, damit MainWindow reagieren kann

    def delete_selected_item(self):
        """Löscht das ausgewählte Lesezeichen oder einen leeren Ordner."""
        selected_items = self.bookmarks_tree_widget.selectedItems()
        if not selected_items:
            return

        current_item = selected_items[0]
        item_data = current_item.data(0, Qt.ItemDataRole.UserRole)

        if not item_data or "type" not in item_data:
            return

        item_type = item_data.get("type")
        item_name_for_dialog = current_item.text(0) # Der angezeigte Name

        if item_type == "bookmark":
            bookmark_id = item_data.get("id")
            if bookmark_id:
                reply = QMessageBox.question(self, "Lesezeichen löschen", 
                                             f"Möchten Sie das Lesezeichen '{item_name_for_dialog}' wirklich löschen?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    if self.bookmark_manager.remove_bookmark(bookmark_id):
                        # populate_bookmarks_tree wird durch das Signal vom Manager aufgerufen
                        pass
                    else:
                         QMessageBox.warning(self, "Fehler", "Lesezeichen konnte nicht gelöscht werden.")
        
        elif item_type == "folder":
            folder_name = item_data.get("name") # Der echte Name aus den Daten, nicht der Anzeigename
            bookmarks_in_folder = self.bookmark_manager.get_bookmarks_by_folder_name(folder_name)
            
            if bookmarks_in_folder:
                QMessageBox.warning(self, "Ordner nicht leer", 
                                    f"Der Ordner '{item_name_for_dialog}' enthält noch Lesezeichen.\n"
                                    "Bitte löschen oder verschieben Sie zuerst die Lesezeichen darin.\n"
                                    "(Das Löschen nicht-leerer Ordner wird noch implementiert.)")
                return
            else: # Leerer Ordner
                reply = QMessageBox.question(self, "Ordner löschen",
                                             f"Möchten Sie den leeren Ordner '{item_name_for_dialog}' wirklich löschen?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    # Hier sollte eine Methode im BookmarkManager aufgerufen werden:
                    # if self.bookmark_manager.remove_folder(folder_name):
                    #     print(f"INFO: Leerer Ordner '{item_name_for_dialog}' gelöscht.")
                    # else:
                    #     QMessageBox.warning(self, "Fehler", "Ordner konnte nicht gelöscht werden.")
                    # Da remove_folder noch nicht robust ist, geben wir nur eine Info aus.
                    QMessageBox.information(self, "Ordner löschen (Hinweis)", 
                                            f"Die Funktion zum expliziten Löschen von Ordnern im Manager ist noch in Entwicklung.\n"
                                            f"Der Ordner '{item_name_for_dialog}' wird nicht mehr angezeigt, wenn er keine Lesezeichen mehr hätte und nicht explizit erstellt wurde.")
                    # Um die Anzeige zu erzwingen, falls der Manager den Ordner nicht mehr liefert:
                    self.populate_bookmarks_tree()


        elif item_type == "folder_unsorted":
            QMessageBox.information(self, "Hinweis", 
                                    f"Der Ordner '{item_name_for_dialog}' kann nicht gelöscht werden. Er dient zur Anzeige unsortierter Lesezeichen.")
            return
        
        self._update_button_states()