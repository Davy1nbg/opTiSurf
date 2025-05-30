from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpacerItem, QSizePolicy, QComboBox
)
from PyQt6.QtCore import QSettings

# NEU: Importiere Konstanten aus config.py
from config import (
    START_PAGE_SETTING_KEY, DEFAULT_START_PAGE,
    HISTORY_DURATION_SETTING_KEY, HISTORY_DURATION_OPTIONS, DEFAULT_HISTORY_DURATION_DAYS
)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen - opTiSurf")
        self.setMinimumWidth(400)

        # APP_ORGANIZATION_NAME und APP_NAME könnten auch aus config.py kommen
        self.settings = QSettings("opTiSurfOrg", "opTiSurf") 

        main_layout = QVBoxLayout(self)

        # --- Startseite Einstellung ---
        start_page_layout = QHBoxLayout()
        start_page_label = QLabel("Startseite URL:")
        self.start_page_edit = QLineEdit()
        start_page_layout.addWidget(start_page_label)
        start_page_layout.addWidget(self.start_page_edit)
        main_layout.addLayout(start_page_layout)

        # --- Verlauf Speicherdauer Einstellung ---
        history_layout = QHBoxLayout()
        history_label = QLabel("Verlauf speichern für:")
        self.history_duration_combo = QComboBox()
        
        for text, days in HISTORY_DURATION_OPTIONS.items(): # Nutzt importierte Konstante
            self.history_duration_combo.addItem(text, userData=days)
            
        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_duration_combo)
        main_layout.addLayout(history_layout)

        # --- Buttons ---
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)

        self._load_settings()

    def _load_settings(self):
        """Lädt die aktuellen Einstellungen und zeigt sie in den UI-Elementen an."""
        start_page_url = self.settings.value(START_PAGE_SETTING_KEY, DEFAULT_START_PAGE) # Nutzt importierte Konstanten
        self.start_page_edit.setText(start_page_url)

        saved_duration_days = self.settings.value(HISTORY_DURATION_SETTING_KEY, 
                                                 DEFAULT_HISTORY_DURATION_DAYS, 
                                                 type=int) # Nutzt importierte Konstanten
        
        index_to_select = -1
        for i in range(self.history_duration_combo.count()):
            if self.history_duration_combo.itemData(i) == saved_duration_days:
                index_to_select = i
                break
        
        if index_to_select != -1:
            self.history_duration_combo.setCurrentIndex(index_to_select)
        else: 
            default_text_key = ""
            for text, days in HISTORY_DURATION_OPTIONS.items(): # Nutzt importierte Konstante
                if days == DEFAULT_HISTORY_DURATION_DAYS: # Nutzt importierte Konstante
                    default_text_key = text
                    break
            if default_text_key: # Überprüfen, ob ein Schlüssel gefunden wurde
                 # Finde den Index des Textes, um sicherzustellen, dass er existiert
                found_idx = self.history_duration_combo.findText(default_text_key)
                if found_idx != -1:
                    self.history_duration_combo.setCurrentIndex(found_idx)

    def accept_settings(self):
        """Speichert die Einstellungen und schließt den Dialog."""
        self.settings.setValue(START_PAGE_SETTING_KEY, self.start_page_edit.text()) # Nutzt importierte Konstante

        selected_index = self.history_duration_combo.currentIndex()
        if selected_index >= 0:
            duration_days_to_save = self.history_duration_combo.itemData(selected_index)
            self.settings.setValue(HISTORY_DURATION_SETTING_KEY, duration_days_to_save) # Nutzt importierte Konstante
        
        super().accept()