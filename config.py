# config.py
# Zentrale Konfigurationskonstanten für die opTiSurf Anwendung

# --- Einstellungen für die Startseite ---
START_PAGE_SETTING_KEY = "general/startPageUrl" # Geändert für bessere Gruppierung in QSettings
DEFAULT_START_PAGE = "https://example.com"

# --- Einstellungen für die Speicherdauer des Verlaufs ---
HISTORY_DURATION_SETTING_KEY = "history/durationDays"
# Optionen: Anzeigetext -> Anzahl der Tage (0 oder negativ für "Immer")
HISTORY_DURATION_OPTIONS = {
    "30 Tage": 30,
    "90 Tage (Standard)": 90,
    "365 Tage (1 Jahr)": 365,
    "Immer behalten": 0 
}
DEFAULT_HISTORY_DURATION_DAYS = 90 # Standardwert in Tagen

# --- Weitere Anwendungs-Konstanten (optional hier zentralisieren) ---
# APP_ORGANIZATION_NAME = "opTiSurfOrg" # Wird in QSettings verwendet
# APP_NAME = "opTiSurf"                 # Wird in QSettings verwendet
# Diese könnten hier definiert und dann in MainWindow und SettingsDialog importiert werden,
# um sicherzustellen, dass QSettings immer dieselben Namen verwendet.