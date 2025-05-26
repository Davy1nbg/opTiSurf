from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen - opTiSurf")
        self.setMinimumWidth(400)

        # QSettings-Objekt erstellen (Organisations- und Anwendungsname)
        self.settings = QSettings("opTiSurfOrg", "opTiSurf") # Dieselben Namen wie in MainWindow verwenden

        layout = QVBoxLayout(self)

        # Startseiten-Eingabefeld
        self.start_page_label = QLabel("Startseiten-URL:")
        self.start_page_edit = QLineEdit()
        # Lade die aktuell gespeicherte Startseite oder einen Standardwert
        current_start_page = self.settings.value("startPageUrl", "https://example.com")
        self.start_page_edit.setText(current_start_page)
        
        layout.addWidget(self.start_page_label)
        layout.addWidget(self.start_page_edit)

        # OK und Abbrechen Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def accept(self):
        new_start_page = self.start_page_edit.text().strip()
        if not new_start_page: 
            new_start_page = "https://example.com" 
        
        if not new_start_page.startswith("http://") and not new_start_page.startswith("https://"):
            new_start_page = "https://" + new_start_page

        self.settings.setValue("startPageUrl", new_start_page)
        super().accept()