import json
import urllib.request
from packaging.version import parse as parse_version
from PyQt6.QtCore import QObject, pyqtSignal

# Diese Konstanten können hier definiert oder beim Instanziieren übergeben werden.
# Für opTiSurf sind sie wahrscheinlich fix.
GITHUB_REPO_OWNER = "davy1nbg"  # Bitte anpassen!
GITHUB_REPO_NAME = "opTiSurf"             # Bitte anpassen!

class UpdateCheckWorker(QObject):
    finished = pyqtSignal(dict) # Signal sendet ein Dictionary mit Ergebnissen

    def __init__(self, current_version_str): # OWNER und REPO werden jetzt von den Konstanten oben genommen
        super().__init__()
        self.current_version_str = current_version_str
        # Man könnte OWNER und REPO auch als Parameter übergeben, wenn sie dynamisch sein müssten:
        # def __init__(self, current_version_str, owner, repo):
        # self.owner = owner
        # self.repo = repo

    def run(self):
        api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"
        result = {
            "update_available": False,
            "latest_version": self.current_version_str,
            "html_url": "",
            "error": None
        }

        try:
            # Hinzufügen eines User-Agent Headers, da manche APIs dies erfordern könnten
            headers = {'User-Agent': f'opTiSurfBrowserUpdateChecker/{self.current_version_str}'}
            req = urllib.request.Request(api_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.load(response)
                    latest_version_str = data.get("tag_name", "").lstrip('v')
                    html_url = data.get("html_url", "")

                    if not latest_version_str:
                        result["error"] = "Kein tag_name im neuesten Release gefunden."
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
            result["error"] = f"Netzwerkfehler oder Timeout: {e.reason}"
        except json.JSONDecodeError:
            result["error"] = "Fehler beim Parsen der API-Antwort (JSON)."
        except Exception as e: # Fange spezifischere Exceptions, wenn möglich
            result["error"] = f"Allgemeiner Fehler beim Update-Check: {str(e)}"
        
        self.finished.emit(result)