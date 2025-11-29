#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dokument Import Optimizer
Prüft und optimiert CSV-Dateien für den Import:
- Prüft ob alle erforderlichen Spalten vorhanden sind
- Ergänzt fehlende Spalten "Abonnements" und "Hosted Datei ID" 
- Entfernt Inhalte aus der Spalte "ID"
- Splittet große Dateien (>950KB) in kleinere Chunks
"""

import csv
import sys
import os
from collections import OrderedDict

# Konstanten
MAX_FILE_SIZE_KB = 950
ROWS_PER_CHUNK = 3800

# Definiere die erwarteten Spalten in der richtigen Reihenfolge
# Mit verschiedenen Sprachversionen
EXPECTED_COLUMNS = [
    ["DokumentUrl*", "Document url*", "URL du document*"],
    ["Verknüpfungsart*", "Url type*", "Type de lien*"],
    ["Abonnements", "Subscriptions"],
    ["Dokumentbeschreibung", "Document description", "Descriptif des documents"],
    ["Sprache*", "Language*", "Langue*"],
    ["Dokumenttyp*", "Document type*", "Type de document*"],
    ["Dokumentnummer", "Document identifier", "Indice du document"],
    ["Ausgabedatum", "Publication date", "Date de publication"],
    ["AcCode*"],
    ["ID"],
    ["Hosted Datei ID", "Hosted file ID", "ID du fichier hébergé"],
    ["Löschen", "Delete", "Supprimer"]
]

def get_column_mapping(header_row):
    """
    Erstellt ein Mapping zwischen den gefundenen Spalten und den erwarteten Spalten
    
    Returns:
        dict: Mapping von gefundenen Spalten zu Standard-Spaltennamen
        list: Liste der erwarteten Spalten in der richtigen Reihenfolge
        list: Liste der fehlenden Spalten
    """
    column_mapping = {}
    standard_columns = []
    found_columns = set()
    
    # Erstelle Standard-Spaltennamen (erste Option aus jeder Liste)
    for col_variations in EXPECTED_COLUMNS:
        standard_columns.append(col_variations[0])
    
    # Finde Übereinstimmungen zwischen Header und erwarteten Spalten
    for header_col in header_row:
        # Entferne Whitespace und BOM (Byte Order Mark) falls vorhanden
        header_col_clean = header_col.strip().lstrip('\ufeff')
        
        for col_variations in EXPECTED_COLUMNS:
            if header_col_clean in col_variations:
                standard_col = col_variations[0]
                column_mapping[header_col] = standard_col
                found_columns.add(standard_col)
                break
    
    # Identifiziere fehlende Spalten
    missing_columns = []
    for standard_col in standard_columns:
        if standard_col not in found_columns:
            missing_columns.append(standard_col)
    
    return column_mapping, standard_columns, missing_columns

def process_csv(input_file, output_file=None):
    """
    Verarbeitet die CSV-Datei:
    - Prüft Spaltenstruktur
    - Ergänzt fehlende Spalten
    - Leert ID-Spalte
    
    Args:
        input_file: Pfad zur Eingabe-CSV-Datei
        output_file: Pfad zur Ausgabe-CSV-Datei (optional)
    """
    
    # Generiere Ausgabedateinamen wenn nicht angegeben
    if output_file is None:
        base_name, extension = os.path.splitext(input_file)
        output_file = f"{base_name}_optimized{extension}"
    
    try:
        # Erkenne die Kodierung
        # utf-8-sig zuerst prüfen, um BOM korrekt zu behandeln
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        file_encoding = None
        
        for encoding in encodings:
            try:
                with open(input_file, 'r', encoding=encoding) as test_file:
                    test_file.read()
                    file_encoding = encoding
                    break
            except UnicodeDecodeError:
                continue
        
        if file_encoding is None:
            print("❌ Fehler: Konnte die Kodierung der Datei nicht erkennen.")
            return False
        
        print(f"📄 Verwende Kodierung: {file_encoding}")
        
        # Lese die CSV-Datei
        with open(input_file, 'r', encoding=file_encoding, newline='') as infile:
            # Erkenne den Delimiter
            sample = infile.read(1024)
            infile.seek(0)
            delimiter = ';' if ';' in sample else ','
            
            print(f"📊 Erkannter Delimiter: '{delimiter}'")
            
            # Lese alle Zeilen
            csv_reader = csv.reader(infile, delimiter=delimiter)
            rows = list(csv_reader)
            
            if len(rows) < 1:
                print("❌ Fehler: Die CSV-Datei ist leer.")
                return False
            
            # Analysiere Header
            original_header = rows[0]
            column_mapping, standard_columns, missing_columns = get_column_mapping(original_header)
            
            print(f"\n📋 Spaltenanalyse:")
            print(f"   Gefundene Spalten: {len(column_mapping)}")
            print(f"   Erwartete Spalten: {len(standard_columns)}")
            
            if missing_columns:
                print(f"\n⚠️  Fehlende Spalten erkannt:")
                for col in missing_columns:
                    print(f"   - {col}")
                
                # Prüfe ob die kritischen Spalten fehlen
                critical_missing = []
                if "Abonnements" in missing_columns:
                    critical_missing.append("Abonnements")
                if "Hosted Datei ID" in missing_columns:
                    critical_missing.append("Hosted Datei ID")
                
                if critical_missing:
                    print(f"\n✅ Folgende Spalten werden ergänzt: {', '.join(critical_missing)}")
            else:
                print("   ✅ Alle erwarteten Spalten vorhanden")
            
            # Erstelle neue Zeilen mit korrekter Spaltenstruktur
            processed_rows = []
            
            # Prüfe ob es mehrere Header-Zeilen gibt (Zeile 2 und 3 sind Übersetzungen)
            has_translated_headers = len(rows) >= 3
            header_rows_count = 1
            
            if has_translated_headers:
                # Prüfe ob Zeile 2 und 3 auch Header sind (keine URLs enthalten)
                row2_looks_like_header = len(rows) > 1 and not any('http' in str(val).lower() for val in rows[1])
                row3_looks_like_header = len(rows) > 2 and not any('http' in str(val).lower() for val in rows[2])
                
                if row2_looks_like_header and row3_looks_like_header:
                    header_rows_count = 3
                    print(f"\n📋 Erkannte Header-Zeilen: 3 (mit Übersetzungen)")
            
            # Erstelle Header-Zeilen
            for header_idx in range(header_rows_count):
                header_row = []
                for col_idx, col_variations in enumerate(EXPECTED_COLUMNS):
                    # Suche ob diese Spalte in der Original-Header existiert
                    found = False
                    for orig_col_idx, orig_header in enumerate(original_header):
                        orig_header_clean = orig_header.strip().lstrip('\ufeff')
                        if orig_header_clean in col_variations:
                            # Spalte existiert - verwende den Wert aus der entsprechenden Zeile
                            if header_idx < len(rows) and orig_col_idx < len(rows[header_idx]):
                                header_row.append(rows[header_idx][orig_col_idx])
                            else:
                                # Fallback: verwende die entsprechende Sprachversion
                                if header_idx < len(col_variations):
                                    header_row.append(col_variations[header_idx])
                                else:
                                    header_row.append(col_variations[0])
                            found = True
                            break
                    
                    if not found:
                        # Spalte fehlt - ergänze mit der entsprechenden Sprachversion
                        if header_idx < len(col_variations):
                            header_row.append(col_variations[header_idx])
                        else:
                            # Fallback auf erste Version wenn keine Übersetzung vorhanden
                            header_row.append(col_variations[0])
                
                processed_rows.append(header_row)
            
            # Variablen für AcCode-Ersetzung
            nautos_code = None
            ac_code_replacements = 0
            
            # Verarbeite Datenzeilen (überspringe Header-Zeilen)
            for row_num, row in enumerate(rows[header_rows_count:], start=header_rows_count + 1):
                new_row = []
                
                # Erstelle ein Dictionary der aktuellen Zeile
                row_data = {}
                for i, value in enumerate(row):
                    if i < len(original_header):
                        orig_col = original_header[i]
                        if orig_col in column_mapping:
                            standard_col = column_mapping[orig_col]
                            row_data[standard_col] = value
                
                # AcCode-Verarbeitung
                if "AcCode*" in row_data:
                    ac_code = row_data["AcCode*"]
                    if ac_code and ac_code.startswith("CS"):
                        if nautos_code is None:
                            print(f"\n⚠️  AcCode mit 'CS' gefunden: {ac_code}")
                            # Versuche Input zu bekommen, Fallback falls kein Terminal
                            try:
                                while True:
                                    code_input = input("   Bitte geben Sie den 3-stelligen Nautos-Code ein: ").strip()
                                    if len(code_input) == 3:
                                        nautos_code = code_input
                                        break
                                    print("   ❌ Bitte genau 3 Zeichen eingeben.")
                            except (EOFError, OSError):
                                print("   ❌ Interaktive Eingabe nicht möglich. Überspringe Ersetzung.")
                                nautos_code = False # Markiere als fehlgeschlagen/übersprungen

                        if nautos_code:
                            # Erstelle neuen Code: CS + 3-stellig + N + Rest ab 6. Zeichen
                            new_prefix = f"CS{nautos_code}N"
                            if len(ac_code) >= 6:
                                new_ac_code = new_prefix + ac_code[6:]
                                row_data["AcCode*"] = new_ac_code
                                ac_code_replacements += 1

                # Fülle neue Zeile in der richtigen Reihenfolge
                for standard_col in standard_columns:
                    if standard_col in row_data:
                        # Spezialbehandlung für ID-Spalte: Inhalt löschen
                        if standard_col == "ID":
                            new_row.append("")  # ID-Inhalt entfernen
                        else:
                            new_row.append(row_data[standard_col])
                    else:
                        # Fehlende Spalte mit leerem Wert ergänzen
                        new_row.append("")
                
                processed_rows.append(new_row)
            
            # Prüfe ob ID-Spalte Inhalte hatte
            id_had_content = False
            if "ID" in column_mapping.values():
                id_index = standard_columns.index("ID")
                for row in rows[1:]:
                    orig_id_index = None
                    for i, header in enumerate(original_header):
                        if header in column_mapping and column_mapping[header] == "ID":
                            orig_id_index = i
                            break
                    if orig_id_index is not None and orig_id_index < len(row):
                        if row[orig_id_index].strip():
                            id_had_content = True
                            break
            
            if id_had_content:
                print("\n🗑️  ID-Spalte: Inhalte wurden entfernt")
            
            # Schreibe die optimierte CSV-Datei
            with open(output_file, 'w', encoding=file_encoding, newline='') as outfile:
                csv_writer = csv.writer(outfile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerows(processed_rows)
            
            print(f"\n✅ Erfolgreich optimiert!")
            print(f"   Eingabe:  {input_file}")
            print(f"   Ausgabe:  {output_file}")
            print(f"   Zeilen:   {len(processed_rows)}")
            
            # Zusammenfassung der Änderungen
            changes_made = []
            if missing_columns and any(col in ["Abonnements", "Hosted Datei ID"] for col in missing_columns):
                changes_made.append("Fehlende Spalten ergänzt")
            if id_had_content:
                changes_made.append("ID-Inhalte gelöscht")
            if ac_code_replacements > 0:
                changes_made.append(f"AcCode angepasst ({ac_code_replacements}x)")
            
            if changes_made:
                print(f"\n📝 Durchgeführte Änderungen:")
                for change in changes_made:
                    print(f"   ✓ {change}")
            else:
                print(f"\n📝 Keine Änderungen notwendig (Datei war bereits optimal)")
            
            # Prüfe Dateigröße und biete Splitting an
            file_size_kb = os.path.getsize(output_file) / 1024
            print(f"\n📊 Dateigröße: {file_size_kb:.1f} KB")
            
            if file_size_kb > MAX_FILE_SIZE_KB:
                print(f"\n⚠️  Die Datei ist größer als {MAX_FILE_SIZE_KB} KB!")
                
                # Frage ob gesplittet werden soll
                try:
                    split_response = input(f"   Soll die Datei in Chunks à {ROWS_PER_CHUNK} Zeilen aufgeteilt werden? [J/n]: ").strip().lower()
                    should_split = split_response in ['', 'j', 'ja', 'y', 'yes']
                except (EOFError, OSError):
                    print("   ❌ Interaktive Eingabe nicht möglich. Überspringe Splitting.")
                    should_split = False
                
                if should_split:
                    # Extrahiere Header-Zeilen (die ersten header_rows_count Zeilen)
                    header_rows = processed_rows[:header_rows_count]
                    data_rows = processed_rows[header_rows_count:]
                    
                    # Berechne Anzahl der Chunks
                    total_data_rows = len(data_rows)
                    num_chunks = (total_data_rows + ROWS_PER_CHUNK - 1) // ROWS_PER_CHUNK
                    
                    print(f"\n📦 Splitting in {num_chunks} Dateien...")
                    
                    base_name, extension = os.path.splitext(output_file)
                    chunk_files = []
                    
                    for chunk_idx in range(num_chunks):
                        start_row = chunk_idx * ROWS_PER_CHUNK
                        end_row = min(start_row + ROWS_PER_CHUNK, total_data_rows)
                        
                        chunk_data = data_rows[start_row:end_row]
                        chunk_rows = header_rows + chunk_data
                        
                        chunk_file = f"{base_name}_part{chunk_idx + 1}{extension}"
                        chunk_files.append(chunk_file)
                        
                        with open(chunk_file, 'w', encoding=file_encoding, newline='') as outfile:
                            csv_writer = csv.writer(outfile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
                            csv_writer.writerows(chunk_rows)
                        
                        chunk_size_kb = os.path.getsize(chunk_file) / 1024
                        print(f"   ✓ {chunk_file} ({len(chunk_data)} Datenzeilen, {chunk_size_kb:.1f} KB)")
                    
                    print(f"\n✅ {num_chunks} Chunk-Dateien erstellt (jeweils mit {header_rows_count}-zeiligem Header)")
            
            return True
            
    except FileNotFoundError:
        print(f"❌ Fehler: Die Datei '{input_file}' wurde nicht gefunden.")
        return False
    except Exception as e:
        print(f"❌ Ein Fehler ist aufgetreten: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion für die Kommandozeilennutzung"""
    
    print("\n" + "="*50)
    print("   DOKUMENT IMPORT OPTIMIZER")
    print("="*50)
    print("Prüft und optimiert CSV-Dateien für den Import")
    print("-"*50 + "\n")
    
    # Prüfe Kommandozeilenargumente
    if len(sys.argv) < 2:
        # Interaktiver Modus
        input_file = input("📁 Bitte geben Sie den Pfad zur CSV-Datei ein: ").strip()
        if not input_file:
            print("❌ Fehler: Kein Dateipfad angegeben.")
            sys.exit(1)
        
        output_response = input("💾 Ausgabedatei (Enter für automatisch generiert): ").strip()
        output_file = output_response if output_response else None
    else:
        # Kommandozeilenargumente verwenden
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Verarbeite die Datei
    if process_csv(input_file, output_file):
        print("\n" + "="*50)
        print("   ✅ VERARBEITUNG ERFOLGREICH")
        print("="*50 + "\n")
    else:
        print("\n" + "="*50)
        print("   ❌ VERARBEITUNG FEHLGESCHLAGEN")
        print("="*50 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()