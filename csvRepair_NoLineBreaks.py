#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Zeilenumbruch-Ersetzer
Ersetzt Zeilenumbrüche innerhalb von CSV-Feldern durch " <br> "
"""

import csv
import sys
import os
import re

def process_csv(input_file, output_file=None):
    """
    Liest eine CSV-Datei und ersetzt Zeilenumbrüche innerhalb von Feldern durch " <br> "
    
    Args:
        input_file: Pfad zur Eingabe-CSV-Datei
        output_file: Pfad zur Ausgabe-CSV-Datei (optional, Standard: input_file_processed.csv)
    """
    
    # Wenn keine Ausgabedatei angegeben, erstelle einen Namen basierend auf der Eingabedatei
    if output_file is None:
        base_name, extension = os.path.splitext(input_file)
        output_file = f"{base_name}_processed{extension}"
    
    try:
        # Erkenne die Kodierung der Datei (meist UTF-8 oder Latin-1 für deutsche Dateien)
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
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
            print(f"Fehler: Konnte die Kodierung der Datei nicht erkennen.")
            return False
        
        print(f"Verwende Kodierung: {file_encoding}")
        
        # Liste für die verarbeiteten Zeilen
        processed_rows = []
        
        # Lese die CSV-Datei
        with open(input_file, 'r', encoding=file_encoding, newline='') as infile:
            # Erkenne den Delimiter (normalerweise ; oder ,)
            sample = infile.read(1024)
            infile.seek(0)
            delimiter = ';' if ';' in sample else ','
            
            print(f"Erkannter Delimiter: '{delimiter}'")
            
            # CSV-Reader mit dem erkannten Delimiter
            csv_reader = csv.reader(infile, delimiter=delimiter)
            
            # Zähler für ersetzte Umbrüche
            total_replacements = 0
            row_num = 0
            
            # Verarbeite jede Zeile
            for row_num, row in enumerate(csv_reader, 1):
                # Ersetze Zeilenumbrüche in jedem Feld
                processed_row = []
                for field in row:
                    # Ersetze alle Arten von Zeilenumbrüchen und zähle sie
                    # Windows (\r\n)
                    count_rn = field.count('\r\n')
                    processed_field = field.replace('\r\n', ' <br> ')
                    
                    # Unix/Linux (\n)
                    count_n = processed_field.count('\n')
                    processed_field = processed_field.replace('\n', ' <br> ')
                    
                    # Mac (\r)
                    count_r = processed_field.count('\r')
                    processed_field = processed_field.replace('\r', ' <br> ')
                    
                    total_replacements += count_rn + count_n + count_r
                    processed_row.append(processed_field)
                
                processed_rows.append(processed_row)
            
            print(f"Verarbeitet: {row_num} Zeilen")
            print(f"Ersetzte Zeilenumbrüche: {total_replacements}")
        
        # Zusätzlicher Schritt: Strichpunkte in quoted Feldern ersetzen und trailing <br> entfernen
        semicolon_replacements = 0
        br_removals = 0
        rows_with_semicolons = []
        
        for row_num, row in enumerate(processed_rows, 1):
            for col_num, field in enumerate(row):
                original_field = field
                
                # Prüfe ob das Feld Strichpunkte enthält (diese würden in CSV gequotet werden)
                if ';' in field:
                    count = field.count(';')
                    semicolon_replacements += count
                    rows_with_semicolons.append((row_num, col_num + 1, field[:50] + "..." if len(field) > 50 else field))
                    row[col_num] = field.replace(';', ':')
                    field = row[col_num]
                
                # Entferne trailing <br> (mit optionalen Leerzeichen davor/danach)
                while True:
                    new_field = re.sub(r'\s*<br>\s*$', '', field)
                    if new_field == field:
                        break
                    br_removals += 1
                    field = new_field
                row[col_num] = field
        
        if rows_with_semicolons:
            print(f"\nZeilen mit Strichpunkten in Spalten (ersetzt durch Doppelpunkt):")
            for row_n, col_n, preview in rows_with_semicolons:
                print(f"  Zeile {row_n}, Spalte {col_n}: {preview}")
        
        print(f"\nErsetzte Strichpunkte in Spalten: {semicolon_replacements}")
        print(f"Entfernte trailing <br>: {br_removals}")
        
        # Schreibe die verarbeitete CSV-Datei
        with open(output_file, 'w', encoding=file_encoding, newline='') as outfile:
            csv_writer = csv.writer(outfile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(processed_rows)
        
        print(f"Erfolgreich gespeichert als: {output_file}")
        return True
        
    except FileNotFoundError:
        print(f"Fehler: Die Datei '{input_file}' wurde nicht gefunden.")
        return False
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return False


def main():
    """Hauptfunktion für die Kommandozeilennutzung"""
    
    print("CSV Zeilenumbruch-Ersetzer")
    print("-" * 40)
    
    # Prüfe Kommandozeilenargumente
    if len(sys.argv) < 2:
        # Interaktiver Modus
        input_file = input("Bitte geben Sie den Pfad zur CSV-Datei ein: ").strip().strip('"\'')
        if not input_file:
            print("Fehler: Kein Dateipfad angegeben.")
            sys.exit(1)
            
        output_file = input("Ausgabedatei (Enter für Standard): ").strip().strip('"\'')
        output_file = output_file if output_file else None
    else:
        # Kommandozeilenargumente verwenden
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Verarbeite die Datei
    if process_csv(input_file, output_file):
        print("\nVerarbeitung erfolgreich abgeschlossen!")
    else:
        print("\nVerarbeitung fehlgeschlagen.")
        sys.exit(1)


if __name__ == "__main__":
    main()
