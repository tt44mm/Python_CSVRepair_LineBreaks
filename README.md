# CSV Zeilenumbruch-Ersetzer

## Beschreibung
Diese Python-Scripts ersetzen Zeilenumbrüche innerhalb von CSV-Feldern durch `" <br> "`, ohne andere Inhalte zu verändern.

## Verfügbare Versionen

### 1. Vollversion (`csv_linebreak_replacer.py`)
- Automatische Encoding-Erkennung (UTF-8, Latin-1, ISO-8859-1, CP1252)
- Automatische Delimiter-Erkennung (`;` oder `,`)
- Interaktiver Modus und Kommandozeilenmodus
- Ausführliche Statusmeldungen

### 2. Einfache Version (`csv_linebreak_replacer_simple.py`)
- Kompakter Code
- Nur Kommandozeilenmodus
- Gleiche Funktionalität

## Installation
Keine zusätzlichen Pakete erforderlich - verwendet nur Python-Standardbibliotheken.

## Verwendung

### Vollversion - Interaktiver Modus:
```bash
python csv_linebreak_replacer.py
```
Das Script fragt dann nach dem Dateipfad.

### Vollversion - Kommandozeilenmodus:
```bash
# Mit automatisch generiertem Ausgabenamen
python csv_linebreak_replacer.py eingabe.csv

# Mit spezifischem Ausgabenamen
python csv_linebreak_replacer.py eingabe.csv ausgabe.csv
```

### Einfache Version:
```bash
python csv_linebreak_replacer_simple.py eingabe.csv ausgabe.csv
```

## Was das Script macht:

1. **Liest die CSV-Datei** mit korrekter Behandlung von Feldern in Anführungszeichen
2. **Ersetzt alle Arten von Zeilenumbrüchen** innerhalb der Felder:
   - Windows-Zeilenumbrüche (`\r\n`)
   - Unix/Linux-Zeilenumbrüche (`\n`)
   - Mac-Zeilenumbrüche (`\r`)
3. **Ersetzt sie durch** `" <br> "`
4. **Speichert die neue CSV** mit demselben Format und Encoding

## Beispiel

### Vorher:
```csv
URL;Beschreibung;Sprache
https://example.com;"ANSI 
TEST UMBRUCH";en
```

### Nachher:
```csv
URL;Beschreibung;Sprache
https://example.com;"ANSI  <br>  TEST UMBRUCH";en
```

## Wichtige Hinweise:

- Das Script behält das originale CSV-Format bei (Delimiter, Encoding, Quoting)
- Nur Zeilenumbrüche INNERHALB von Feldern werden ersetzt
- Die Struktur der CSV-Datei bleibt erhalten
- Es werden automatisch verschiedene Encodings getestet (wichtig für deutsche Umlaute)

## Fehlerbehebung:

1. **"Datei nicht gefunden"**: Überprüfen Sie den Dateipfad
2. **Encoding-Fehler**: Das Script testet automatisch mehrere Encodings
3. **Falsche Ausgabe**: Prüfen Sie, ob der richtige Delimiter erkannt wurde

## Für Ihre spezifische CSV:

Das Script wurde für CSV-Dateien wie Ihre Beispieldatei optimiert:
- Delimiter: `;` (Semikolon)
- Mehrzeilige Felder in Anführungszeichen
- Deutsche Umlaute
- Verschiedene Zeilenumbruch-Typen
