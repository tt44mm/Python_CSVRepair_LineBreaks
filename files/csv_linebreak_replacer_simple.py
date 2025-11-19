#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher CSV Zeilenumbruch-Ersetzer
"""

import csv
import sys

def replace_linebreaks_in_csv(input_file, output_file):
    """
    Ersetzt Zeilenumbrüche in CSV-Feldern durch <br> Tags
    """
    # Versuche verschiedene Encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(input_file, 'r', encoding=encoding, newline='') as infile:
                # Erkenne Delimiter
                sample = infile.read(1024)
                infile.seek(0)
                delimiter = ';' if ';' in sample else ','
                
                # Lese alle Zeilen
                reader = csv.reader(infile, delimiter=delimiter)
                rows = []
                
                for row in reader:
                    # Ersetze Zeilenumbrüche in jedem Feld
                    processed_row = [
                        field.replace('\r\n', ' <br> ')
                             .replace('\n', ' <br> ')
                             .replace('\r', ' <br> ')
                        for field in row
                    ]
                    rows.append(processed_row)
                
                # Schreibe Ausgabedatei
                with open(output_file, 'w', encoding=encoding, newline='') as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
                    writer.writerows(rows)
                
                print(f"✓ Datei erfolgreich verarbeitet")
                print(f"  Eingabe: {input_file}")
                print(f"  Ausgabe: {output_file}")
                print(f"  Encoding: {encoding}")
                print(f"  Delimiter: '{delimiter}'")
                print(f"  Zeilen: {len(rows)}")
                return True
                
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Fehler: {e}")
            return False
    
    print("Fehler: Konnte Datei-Encoding nicht erkennen")
    return False


# Hauptprogramm
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python script.py eingabe.csv ausgabe.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not replace_linebreaks_in_csv(input_file, output_file):
        sys.exit(1)
