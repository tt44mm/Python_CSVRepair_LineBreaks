#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dokument Import Optimizer
Prüft und optimiert CSV-Dateien für den Import:
- Prüft ob alle erforderlichen Spalten vorhanden sind
- Ergänzt fehlende Spalten "Abonnements" und "Hosted Datei ID" 
- Entfernt Inhalte aus der Spalte "ID"
"""

import csv
import sys
import os
from collections import OrderedDict

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
        header_col_clean = header_col.strip()
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
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']
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
            
            # Erstelle neuen Header
            processed_rows.append(standard_columns)
            
            # Verarbeite Datenzeilen
            for row_num, row in enumerate(rows[1:], start=2):
                new_row = []
                
                # Erstelle ein Dictionary der aktuellen Zeile
                row_data = {}
                for i, value in enumerate(row):
                    if i < len(original_header):
                        orig_col = original_header[i]
                        if orig_col in column_mapping:
                            standard_col = column_mapping[orig_col]
                            row_data[standard_col] = value
                
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
            
            if changes_made:
                print(f"\n📝 Durchgeführte Änderungen:")
                for change in changes_made:
                    print(f"   ✓ {change}")
            else:
                print(f"\n📝 Keine Änderungen notwendig (Datei war bereits optimal)")
            
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