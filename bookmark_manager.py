import json
import os
import uuid # Für eindeutige IDs
from PyQt6.QtCore import QObject, pyqtSignal, QStandardPaths # QDir wird hier nicht direkt verwendet

# Konstante für den Anwendungs-spezifischen Datenordnernamen
APP_DATA_SUBFOLDER = "opTiSurf"
BOOKMARKS_FILENAME = "bookmarks.json"
FALLBACK_BOOKMARKS_FILENAME = "bookmarks_fallback.json"

class BookmarkManager(QObject):
    """
    Verwaltet Lesezeichen und deren Zuordnung zu Ordnern.
    Speichert Daten in einer JSON-Datei im Anwendungsdatenverzeichnis.
    Signalisiert Änderungen über `bookmarks_changed`.
    """
    bookmarks_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bookmarks_file_path = self._get_data_file_path()
        self.bookmarks: list[dict] = []
        self.explicit_folders: set[str] = set()
        self.load_data()

    def _get_data_file_path(self) -> str:
        """Ermittelt den Pfad zur Datendatei und stellt sicher, dass der Ordner existiert."""
        try:
            app_data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
            if not app_data_dir:
                print(f"WARNUNG: Standard '{QStandardPaths.StandardLocation.AppDataLocation.name}' konnte nicht ermittelt werden. Verwende aktuelles Verzeichnis als Fallback.")
                app_data_dir = "." # Fallback ins aktuelle Verzeichnis
            
            specific_app_data_path = os.path.join(app_data_dir, APP_DATA_SUBFOLDER)
            
            if not os.path.exists(specific_app_data_path):
                os.makedirs(specific_app_data_path, exist_ok=True)
                print(f"INFO: Datenverzeichnis '{specific_app_data_path}' erstellt.")
            
            return os.path.join(specific_app_data_path, BOOKMARKS_FILENAME)

        except Exception as e:
            print(f"FEHLER: Kritischer Fehler beim Ermitteln des Datenspeicherpfads: {e}")
            return os.path.join(".", FALLBACK_BOOKMARKS_FILENAME) # Sicherer Fallback

    def load_data(self):
        """Lädt Lesezeichen und explizite Ordner aus der JSON-Datei."""
        self.bookmarks = []
        self.explicit_folders = set()
        
        if not os.path.exists(self._bookmarks_file_path):
            print(f"INFO: Keine Datendatei ({self._bookmarks_file_path}) gefunden. Starte mit leeren Daten.")
            self.bookmarks_changed.emit() # Auch bei leeren Daten UI informieren
            return

        try:
            with open(self._bookmarks_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict): # Erwarte immer ein Dictionary (neues Format)
                if isinstance(data, list): # Altes Format: Nur Lesezeichen-Liste
                    print("INFO: Altes Lesezeichenformat erkannt. Konvertiere und baue Ordnerliste neu auf.")
                    loaded_bookmarks_list = data
                    loaded_explicit_folders = set() # Keine expliziten Ordner im alten Format
                else:
                    print(f"WARNUNG: Unerwartetes Root-Format in {self._bookmarks_file_path}. Starte mit leeren Daten.")
                    loaded_bookmarks_list = []
                    loaded_explicit_folders = set()
            else: # Neues Format (Dictionary)
                loaded_bookmarks_list = data.get('bookmarks', [])
                loaded_explicit_folders = set(data.get('explicit_folders', []))

            temp_bookmarks = []
            for bm_data in loaded_bookmarks_list:
                if not isinstance(bm_data, dict):
                    print(f"WARNUNG: Ungültiger Lesezeichen-Eintrag übersprungen (kein Dictionary): {bm_data}")
                    continue
                
                # Stelle Standardwerte sicher und füge ggf. 'folder_name' hinzu
                bm_id = bm_data.get('id', str(uuid.uuid4()))
                bm_title = bm_data.get('title', bm_data.get('url', 'Unbenannt')) # Titel oder URL als Fallback
                bm_url = bm_data.get('url')
                bm_folder = bm_data.get('folder_name') # Kann None sein

                if not bm_url: # Lesezeichen ohne URL sind ungültig
                    print(f"WARNUNG: Lesezeichen ohne URL übersprungen: {bm_title}")
                    continue

                temp_bookmarks.append({
                    'id': bm_id,
                    'title': bm_title,
                    'url': bm_url,
                    'folder_name': bm_folder.strip() if isinstance(bm_folder, str) and bm_folder.strip() else None
                })
                # Füge auch implizite Ordner zu den expliziten hinzu
                if bm_folder and isinstance(bm_folder, str) and bm_folder.strip():
                    loaded_explicit_folders.add(bm_folder.strip())
            
            self.bookmarks = temp_bookmarks
            self.explicit_folders = loaded_explicit_folders
            print(f"INFO: Daten erfolgreich geladen aus {self._bookmarks_file_path}")

        except json.JSONDecodeError:
            print(f"FEHLER: Fehler beim Dekodieren von JSON aus {self._bookmarks_file_path}.")
        except Exception as e:
            print(f"FEHLER: Unbekannter Fehler beim Laden der Daten: {e}")
        
        self.bookmarks_changed.emit()

    def save_data(self):
        """Speichert die aktuellen Lesezeichen und expliziten Ordner in die JSON-Datei."""
        data_to_save = {
            "explicit_folders": sorted(list(self.explicit_folders)),
            "bookmarks": self.bookmarks
        }
        try:
            with open(self._bookmarks_file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4, sort_keys=True) # sort_keys für konsistente Reihenfolge
            print(f"INFO: Daten gespeichert in {self._bookmarks_file_path}")
        except Exception as e:
            print(f"FEHLER: Konnte Daten nicht in {self._bookmarks_file_path} speichern: {e}")

    def add_bookmark(self, title: str, url: str, folder_name: str = None) -> bool:
        """Fügt ein neues Lesezeichen hinzu und stellt sicher, dass der Ordner bekannt ist."""
        if not title.strip() and url: # Wenn Titel leer ist, URL als Titel nehmen
            title = url
        elif not title.strip() and not url: # Ungültiger Aufruf
             print("WARNUNG: Versuch, Lesezeichen ohne Titel und URL hinzuzufügen.")
             return False

        clean_folder_name = folder_name.strip() if isinstance(folder_name, str) and folder_name.strip() else None

        if clean_folder_name:
            self.explicit_folders.add(clean_folder_name) # Ordner als explizit bekannt machen

        new_bookmark = {
            "id": str(uuid.uuid4()),
            "title": title.strip(),
            "url": url,
            "folder_name": clean_folder_name
        }
        self.bookmarks.append(new_bookmark)
        self.save_data()
        self.bookmarks_changed.emit()
        print(f"INFO: Lesezeichen hinzugefügt: '{new_bookmark['title']}' zu Ordner: '{clean_folder_name}'")
        return True

    def remove_bookmark(self, bookmark_id: str) -> bool:
        """Entfernt ein Lesezeichen anhand seiner ID."""
        initial_len = len(self.bookmarks)
        self.bookmarks = [bm for bm in self.bookmarks if bm.get("id") != bookmark_id]
        if len(self.bookmarks) < initial_len:
            self.save_data()
            self.bookmarks_changed.emit()
            # Der Ordner bleibt in explicit_folders, auch wenn er leer wird.
            # Das Löschen von leeren Ordnern wäre eine separate Logik in remove_folder.
            print(f"INFO: Lesezeichen mit ID '{bookmark_id}' entfernt.")
            return True
        print(f"WARNUNG: Lesezeichen mit ID '{bookmark_id}' nicht gefunden zum Entfernen.")
        return False

    def get_all_bookmarks(self) -> list[dict]:
        return list(self.bookmarks) # Gibt eine Kopie zurück

    def get_bookmark_by_id(self, bookmark_id: str) -> dict | None:
        for bm in self.bookmarks:
            if bm.get("id") == bookmark_id:
                return bm
        return None

    def get_folder_names(self) -> list[str]:
        """Gibt eine Liste aller eindeutigen, bekannten Ordnernamen zurück."""
        # Sammle zuerst alle Ordnernamen aus den Lesezeichen
        folder_names_from_bookmarks = set()
        for bm in self.bookmarks:
            folder = bm.get("folder_name")
            if folder: # Stellt sicher, dass es nicht None oder leer ist nach strip() in add_bookmark
                folder_names_from_bookmarks.add(folder)
        
        # Kombiniere mit explizit erstellten Ordnern und sortiere
        all_folder_names = self.explicit_folders.union(folder_names_from_bookmarks)
        return sorted(list(all_folder_names))

    def get_bookmarks_by_folder_name(self, folder_name: str | None) -> list[dict]:
        """Gibt Lesezeichen für einen Ordnernamen oder unsortierte Lesezeichen (wenn folder_name None ist) zurück."""
        target_folder = folder_name.strip() if isinstance(folder_name, str) and folder_name.strip() else None
        return [bm for bm in self.bookmarks if bm.get("folder_name") == target_folder]

    def create_folder(self, folder_name: str) -> bool:
        """Fügt einen Ordnernamen zur Liste der expliziten Ordner hinzu."""
        if not folder_name or not isinstance(folder_name, str) or not folder_name.strip():
            print("WARNUNG: Ungültiger Ordnername für create_folder.")
            return False
        
        clean_folder_name = folder_name.strip()
        if clean_folder_name not in self.explicit_folders: # Nur hinzufügen, wenn noch nicht explizit da
            self.explicit_folders.add(clean_folder_name)
            self.save_data()
            self.bookmarks_changed.emit() # UI über mögliche Änderung der Ordnerliste informieren
            print(f"INFO: Ordner '{clean_folder_name}' explizit erstellt/registriert.")
            return True
        print(f"INFO: Ordner '{clean_folder_name}' existiert bereits explizit.")
        return False # Kein Fehler, aber auch nichts geändert, wenn schon da