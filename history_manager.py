import sqlite3
import datetime
import os
import traceback # Für detaillierte Fehlerinformationen im Log
from PyQt6.QtCore import QObject, pyqtSignal, QStandardPaths

APP_DATA_SUBFOLDER = "opTiSurf"
HISTORY_DB_FILENAME = "history.db"
CLEANUP_LOG_FILENAME = "opTiSurf_history_cleanup.log" # Eigene Log-Datei für diese Funktion

class HistoryManager(QObject):
    history_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db_path = self._get_db_path()
        # Log-Datei-Pfad initialisieren
        self._cleanup_log_path = os.path.join(os.path.dirname(self._db_path), CLEANUP_LOG_FILENAME)
        try: # Alte Log-Datei löschen für frische Logs bei jedem Start der Manager-Instanz
            if os.path.exists(self._cleanup_log_path):
                os.remove(self._cleanup_log_path)
        except OSError:
            pass # Ignoriere Fehler beim Löschen der Log-Datei

        self._ensure_db_table()
        print(f"INFO [History]: HistoryManager initialisiert. DB-Pfad: {self._db_path}")

    def _log_cleanup_debug(self, message):
        """Schreibt Debug-Nachrichten in die Konsole und eine separate Log-Datei."""
        print(message)
        try:
            with open(self._cleanup_log_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now().isoformat()} - {message}\n")
        except Exception as e:
            print(f"FEHLER [HistoryLog]: Konnte nicht in Cleanup-Log schreiben: {e}")

    # ... (_get_db_path, _execute_query, _fetch_query, _ensure_db_table bleiben gleich) ...
    def _get_db_path(self) -> str:
        try:
            app_data_dir_obj = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
            if not app_data_dir_obj:
                app_data_dir = "." 
                print(f"WARNUNG [History]: Standard AppDataLocation nicht gefunden, verwende aktuelles Verzeichnis für DB.")
            else:
                app_data_dir = app_data_dir_obj
            specific_app_data_path = os.path.join(app_data_dir, APP_DATA_SUBFOLDER)
            if not os.path.exists(specific_app_data_path):
                os.makedirs(specific_app_data_path, exist_ok=True)
                print(f"INFO [History]: Datenverzeichnis '{specific_app_data_path}' für DB erstellt.")
            return os.path.join(specific_app_data_path, HISTORY_DB_FILENAME)
        except Exception as e:
            print(f"FEHLER [History]: Kritischer Fehler beim Ermitteln des DB-Pfads: {e}")
            return os.path.join(".", "history_fallback.db")

    def _execute_query(self, query: str, params: tuple = ()) -> bool:
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            self._log_cleanup_debug(f"FEHLER [History] bei DB-Schreibzugriff: {e}\nQuery: {query}\nParams: {params}")
            print(f"FEHLER [History] bei DB-Schreibzugriff: {e}\nQuery: {query}\nParams: {params}")
            return False

    def _fetch_query(self, query: str, params: tuple = ()) -> list:
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall() 
        except sqlite3.Error as e:
            self._log_cleanup_debug(f"FEHLER [History] bei DB-Lesezugriff: {e}\nQuery: {query}\nParams: {params}")
            print(f"FEHLER [History] bei DB-Lesezugriff: {e}\nQuery: {query}\nParams: {params}")
            return []

    def _ensure_db_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS history_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            visit_timestamp TEXT NOT NULL UNIQUE 
        );
        """
        if self._execute_query(create_table_query):
            self._execute_query("CREATE INDEX IF NOT EXISTS idx_history_url ON history_visits (url);")
            self._execute_query("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history_visits (visit_timestamp DESC);")
            # print("INFO [History]: Datenbanktabelle 'history_visits' sichergestellt.") # Reduziere Logging hier


    def add_visit(self, url: str, title: str | None):
        # ... (Diese Methode bleibt gleich) ...
        if not url or url.startswith("about:") or not url.strip():
            return
        last_visits = self.get_history_entries(limit=1)
        if last_visits:
            last_entry_url, _, last_entry_ts_str = last_visits[0]
            if last_entry_url == url:
                try:
                    # last_ts wird offset-aware sein, wenn der gespeicherte String Zeitzoneninfo hatte (z.B. von .isoformat() bei einem UTC-Datetime)
                    last_ts = datetime.datetime.fromisoformat(last_entry_ts_str)
                    
                    # Aktuelle Zeit als offset-aware UTC holen
                    now_utc = datetime.datetime.now(datetime.timezone.utc)

                    # Stelle sicher, dass last_ts auch UTC ist, wenn es offset-aware ist.
                    # Wenn fromisoformat einen UTC-Zeitstempel korrekt geparst hat, sollte es das sein.
                    # Für den Moment gehen wir davon aus, dass last_ts von isoformat (falls es TZ-Infos hatte) bereits UTC ist.

                    if (now_utc - last_ts).total_seconds() < 60:
                        return
                except ValueError:
                    pass 
        timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        title_to_save = title.strip() if isinstance(title, str) and title.strip() else ""
        query = "INSERT INTO history_visits (url, title, visit_timestamp) VALUES (?, ?, ?)"
        if self._execute_query(query, (url, title_to_save, timestamp_str)):
            self.history_changed.emit()
            
    def get_history_entries(self, limit: int = 100, offset: int = 0, sort_desc: bool = True) -> list:
        # ... (Diese Methode bleibt gleich) ...
        order = "DESC" if sort_desc else "ASC"
        query = f"SELECT url, title, visit_timestamp FROM history_visits ORDER BY visit_timestamp {order} LIMIT ? OFFSET ?"
        rows = self._fetch_query(query, (limit, offset))
        return rows 

    def clear_all_history(self) -> bool:
        # ... (Diese Methode bleibt gleich, ruft _execute_query auf) ...
        if self._execute_query("DELETE FROM history_visits"):
            self._log_cleanup_debug("INFO [History]: Gesamter Verlauf gelöscht.")
            self._log_cleanup_debug("INFO [History]: Führe VACUUM aus...")
            if self._execute_query("VACUUM;"):
                 self._log_cleanup_debug("INFO [History]: VACUUM erfolgreich.")
            else:
                 self._log_cleanup_debug("WARNUNG [History]: VACUUM konnte nicht ausgeführt werden.")
            self.history_changed.emit()
            return True
        return False

    def search_history(self, search_term: str, limit: int = 100) -> list:
        # ... (Diese Methode bleibt gleich) ...
        query = "SELECT url, title, visit_timestamp FROM history_visits WHERE url LIKE ? OR title LIKE ? ORDER BY visit_timestamp DESC LIMIT ?"
        term = f"%{search_term}%" 
        rows = self._fetch_query(query, (term, term, limit))
        return rows

    # --- MODIFIZIERTE METHODE MIT DETAILLIERTEM LOGGING ---
    def cleanup_old_history_entries(self, days_to_keep: int) -> int:
        self._log_cleanup_debug(f"--- cleanup_old_history_entries AUFGERUFEN mit days_to_keep: {days_to_keep} ---")
        
        if days_to_keep <= 0:
            self._log_cleanup_debug("INFO [HistoryCleanup]: Keine Aufräumarbeiten, da days_to_keep <= 0.")
            return 0

        rows_deleted = 0
        try:
            cutoff_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_to_keep)
            self._log_cleanup_debug(f"INFO [HistoryCleanup]: Berechnetes Cutoff-Datum (UTC): {cutoff_dt.isoformat()}")
            cutoff_timestamp_str = cutoff_dt.isoformat()
            
            query = "DELETE FROM history_visits WHERE visit_timestamp < ?"
            self._log_cleanup_debug(f"INFO [HistoryCleanup]: SQL DELETE Query wird vorbereitet: {query} mit Parameter: {cutoff_timestamp_str}")
            
            conn = None
            try:
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()
                self._log_cleanup_debug("INFO [HistoryCleanup]: Führe DELETE-Query aus...")
                cursor.execute(query, (cutoff_timestamp_str,))
                rows_deleted = cursor.rowcount
                self._log_cleanup_debug(f"INFO [HistoryCleanup]: DELETE-Query ausgeführt. {rows_deleted} Zeilen betroffen (vor commit).")
                conn.commit()
                self._log_cleanup_debug("INFO [HistoryCleanup]: Commit nach DELETE erfolgreich.")
                
                if rows_deleted > 0:
                    self._log_cleanup_debug(f"INFO [HistoryCleanup]: {rows_deleted} Verlaufseinträge älter als {days_to_keep} Tage zum Löschen markiert.")
                    self._log_cleanup_debug("INFO [HistoryCleanup]: Führe VACUUM aus...")
                    cursor.execute("VACUUM;")
                    conn.commit() # Commit nach VACUUM
                    self._log_cleanup_debug("INFO [HistoryCleanup]: VACUUM und Commit erfolgreich.")
                    self.history_changed.emit()
                else:
                    self._log_cleanup_debug("INFO [HistoryCleanup]: Keine alten Einträge zum Löschen gefunden.")
            except sqlite3.Error as e_sql:
                self._log_cleanup_debug(f"--- SQL EXCEPTION in cleanup_old_history_entries ---\n{str(e_sql)}\nQuery: {query}\n{traceback.format_exc()}\n------------------------------------------")
            finally:
                if conn:
                    conn.close()
                    self._log_cleanup_debug("INFO [HistoryCleanup]: Datenbankverbindung geschlossen.")
            
            self._log_cleanup_debug(f"INFO [HistoryCleanup]: cleanup_old_history_entries beendet. {rows_deleted} Einträge gelöscht.")
            return rows_deleted
            
        except Exception as e_general:
            self._log_cleanup_debug(f"--- ALLGEMEINE EXCEPTION in cleanup_old_history_entries ---\n{str(e_general)}\n{traceback.format_exc()}\n------------------------------------------")
            return 0