import csv

input_file = r"x:\DEVELOPMENTS\Python_CSVRepair_LineBreaks\jh_processed.csv"
encoding = 'utf-8'

with open(input_file, 'r', encoding=encoding, newline='') as infile:
    sample = infile.read(1024)
    infile.seek(0)
    delimiter = ';' if ';' in sample else ','
    
    csv_reader = csv.reader(infile, delimiter=delimiter)
    rows = list(csv_reader)
    header = rows[0]
    
    print(f"First column raw: {repr(header[0])}")
    print(f"First column stripped: {repr(header[0].strip())}")
    
    expected = "DokumentUrl*"
    print(f"Expected: {repr(expected)}")
    print(f"Match? {header[0].strip() == expected}")
