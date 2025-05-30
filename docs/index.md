# Willkommen bei opTiSurf Browser!

Aktuelle Version: 0.5.0

opTiSurf ist ein Webbrowser-Projekt, das mit Python und PyQt entwickelt wird. 
Hier findet ihr Infos zu aktuellen und geplanten Features.

## Hinweise zur Installation

Hallo liebe opTiSurf Nutzer,

vielen Dank, dass ihr opTiSurf ausprobieren möchtet! Beim Ausführen der Installationsdatei (opTiSurf_installer.exe) werdet ihr wahrscheinlich eine Sicherheitswarnung von Windows sehen, die besagt, dass der "Herausgeber unbekannt" ist oder der "Windows SmartScreen-Filter die Ausführung verhindert hat".

Warum erscheint diese Meldung?

Das ist eine Standard-Sicherheitsmaßnahme von Windows für Software, die von kleineren, unabhängigen Entwicklern wie mir stammt und nicht mit einem teuren, kommerziellen digitalen Zertifikat signiert wurde. Es bedeutet nicht, dass die Software unsicher ist, sondern nur, dass Windows den Herausgeber (also mich) nicht automatisch als großes Softwareunternehmen erkennt. Ich versichere euch, dass die Installationsdatei, die ihr von meiner offiziellen opTiSurf-Seite (z.B. GitHub Releases) heruntergeladen habt, sicher ist.

So könnt ihr die Installation trotzdem sicher durchführen:

Je nachdem, welche Meldung ihr seht, sind die Schritte leicht unterschiedlich:

Wenn der Windows SmartScreen-Filter erscheint (oft ein blaues Fenster):
    Klickt bitte nicht direkt auf "Nicht ausführen".
    Sucht stattdessen nach einem Link oder einer Option mit der Aufschrift "Weitere Informationen" (manchmal auch "More info"). Klickt darauf.
    Danach sollte ein neuer Button erscheinen, der "Trotzdem ausführen" (oder "Run anyway") heißt. Diesen könnt ihr dann anklicken, um die Installation zu starten.

Wenn eine Meldung der Benutzerkontensteuerung (UAC) mit "Unbekannter Herausgeber" erscheint:
    Diese Meldung fragt, ob ihr zulassen möchtet, dass diese App von einem unbekannten Herausgeber Änderungen an eurem Gerät vornimmt.
    Um opTiSurf zu installieren, klickt hier bitte auf "Ja".

Ich stecke viel Arbeit und Herzblut in opTiSurf und möchte euch ein tolles Browser-Erlebnis bieten. Diese Windows-Warnungen sind für kleine Projekte wie dieses leider erstmal normal.

Vielen Dank für euer Verständnis und Vertrauen! Ich freue mich auf euer Feedback zu opTiSurf.

Viele Grüße,
David Pierzyna

## Download
* [opTiSurf Setup v0.5.0](https://github.com/Davy1nbg/opTiSurf/releases/download/v0.5.0/opTiSurf_installer.exe)


## Änderungen Release v0.5.0

Dein Browserverlauf – Intelligent, Sicher und Anpassbar!

Mit der neuesten Version von opTiSurf führen wir eine umfassend überarbeitete Browserverlaufs-Funktion ein! Wir wissen, wie wichtig es ist, besuchte Webseiten einfach wiederzufinden und gleichzeitig die Kontrolle über die eigenen Daten zu behalten. Deshalb haben wir den Verlauf so gestaltet, dass er sowohl zuverlässig als auch flexibel ist.

Das bietet dir der neue Browserverlauf von opTiSurf:

Zuverlässige und Robuste Speicherung:
Jede von dir besuchte Webseite (mit Titel, URL und genauem Zeitstempel) wird automatisch in einer lokalen Datenbank auf deinem Computer gespeichert. Diese Methode sorgt für eine stabile und performante Verwaltung deiner Daten, auch wenn sich mit der Zeit viele Einträge ansammeln.

Volle Kontrolle über die Speicherdauer – Du entscheidest!
Nicht jeder möchte seinen Browserverlauf unbegrenzt aufbewahren. In den Einstellungen von opTiSurf kannst du jetzt genau festlegen, wie lange deine Verlaufsdaten gespeichert werden sollen:
* Optionen: Wähle zwischen "30 Tagen", "90 Tagen (Standard)", "365 Tagen (1 Jahr)" oder "Immer behalten".
* Automatische Bereinigung: Wenn du eine begrenzte Speicherdauer einstellst, kümmert sich opTiSurf automatisch im Hintergrund darum, ältere Einträge zu entfernen. Das hält deine Verlaufsdatenbank schlank und performant, ohne dass du manuell eingreifen musst.

Übersichtlicher Verlaufs-Manager:
Über das Menü "Verlauf" > "Gesamten Verlauf anzeigen..." gelangst du zu einer klar strukturierten Ansicht deiner besuchten Seiten. Dort siehst du übersichtlich:
* Den Titel der Seite
* Die vollständige URL
* Den genauen Zeitpunkt deines letzten Besuchs

Einfache Interaktion mit deinem Verlauf:
* Direkt öffnen: Mit einem Doppelklick oder über den "Öffnen"-Button im Verlaufs-Manager kannst du jede Seite sofort   wieder im Browser laden.
* URL kopieren: Kopiere die Adresse eines Verlaufseintrags mit einem Klick in deine Zwischenablage.
* Gesamten Verlauf löschen: Wenn du einen sauberen Schnitt machen möchtest, kannst du deinen gesamten Browserverlauf sicher und unwiderruflich entfernen.

Mit diesem intelligenten und anpassbaren Verlauf möchten wir dir nicht nur helfen, wichtige Informationen schnell wiederzufinden, sondern dir auch die volle Kontrolle darüber geben, wie deine Browserdaten verwaltet werden. Zukünftige Updates werden weitere Verwaltungsoptionen bringen, wie das Löschen einzelner Einträge und eine Suchfunktion im Verlauf!

## Aktuelle Features
* NEU: Browserverlauf
    - Automatische Protokollierung: Speichert besuchte Webseiten (Titel, URL, Zeitstempel) zuverlässig in einer lokalen Datenbank.
    - Kontrollierte Speicherdauer: Wähle in den Einstellungen, wie lange dein Verlauf aufbewahrt wird (30, 90, 365     Tage oder immer). Ältere Einträge werden automatisch bereinigt.
    - Übersichtlicher Verlaufs-Manager: Zeige alle Einträge sortiert mit Titel, URL und Besuchszeit an.
    - Einfache Aktionen:
    * Seiten direkt aus dem Verlauf öffnen.
    * URLs in die Zwischenablage kopieren.
    * Gesamten Verlauf sicher löschen.

* Lesezeichen-Verwaltung
* Surfen im Web mit moderner Chromium-basierter Engine
* Intuitive Navigation (Adressleiste, Vorwärts, Zurück, Neu laden, Stopp)
* Persönlich anpassbare Startseite
* Dynamischer Fenstertitel (zeigt den Titel der Webseite an)
* Integrierte Benachrichtigung über neue Browser-Versionen


## Geplante Features
* Blockieren von Drittanbieter-Cookies für mehr Privatsphäre
* Ladefortschrittsanzeige
* Zugriff auf Downloads-Ordner und den Ordner für die heruntergeladenen Dateien selbst festlegen

## Feedback
Habt ihr Ideen oder Fehler gefunden? Sagt mir einfach Bescheid!

---

Letzte Aktualisierung: 30. Mai 2025
