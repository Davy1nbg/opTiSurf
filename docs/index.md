# Willkommen bei opTiSurf Browser!

Aktuelle Version: 0.3.1

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
* [opTiSurf Setup v0.3.1](https://github.com/Davy1nbg/opTiSurf/releases/download/v0.3.1/opTiSurf_installer.exe)

=======

## Änderungen Release v0.3.1
* Quality Update: Refactoring der Update-Prüfung & Auslagerung des Update-Checkers in eine eigene Datei

## Aktuelle Features
* NEU: Automatische Update-Prüfung und -Benachrichtigung: opTiSurf prüft jetzt beim Start automatisch, ob eine neue Version zum Download bereitsteht. Zusätzlich können Sie jederzeit manuell über das Menü 'Hilfe' -> 'Nach Updates suchen...' eine Prüfung anstoßen. Ist ein Update verfügbar, erhalten Sie eine Benachrichtigung mit einem direkten Link zur Download-Seite. (Die Installation des Updates erfolgt weiterhin manuell.)
* Surfen im Web mit Chromium-Engine
* Adressleiste zur URL-Eingabe
* Navigationsbuttons (Vor, Zurück, Neu laden, Stopp)
* Dynamische Anpassung des Fenstertitels
* Einstellbare Startseite (wird persistiert, die Einstellung ist auch nach einem Neustart verfügbar)


## Geplante Features
* Blockieren von Drittanbieter-Cookies für mehr Privatsphäre
* Ladefortschrittsanzeige
* Lesezeichen setzen und verwalten
* Zugriff auf downloads-Ordner und den Ordner für die heruntergeladenen Dateien selbst festlegen

## Feedback
Habt ihr Ideen oder Fehler gefunden? Sagt mir einfach Bescheid!

---

Letzte Aktualisierung: 28. Mai 2025
