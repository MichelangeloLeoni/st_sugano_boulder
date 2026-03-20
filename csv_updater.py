import csv

INPUT_CSV = "raw_blocks_data.csv"
OUTPUT_CSV = "data/blocchi.csv"

def convert_to_decimal(coord):
    """Converti coordinate da gradi, minuti, secondi a decimali"""
    try:
        parts = coord.split()
        if len(parts) == 3:  # Formato D M S
            degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            return degrees + (minutes / 60) + (seconds / 3600)
        elif len(parts) == 2:  # Formato D M
            degrees = float(parts[0])
            minutes = float(parts[1])
            return degrees + (minutes / 60)
        else:  # Formato D
            return float(coord)
    except Exception as e:
        print(f"Errore nella conversione della coordinata '{coord}': {e}")
        return None

def update_csv(input_file, output_file):
    """Trasferisci i dati da un csv all'altro ma converti i campi lat e lon"""
    with open(input_file, mode='r', encoding='utf-8') as infile, \
         open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = ['lat','lon','settore','sasso','faccia','nome','numero','grado','partenza','fa','immagine','topos','descrizione','tag']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            # Converti lat e lon da gradi a decimali
            lat = convert_to_decimal(row['lat'])
            lon = convert_to_decimal(row['lon'])
            writer.writerow({
                'lat': lat,
                'lon': lon,
                'settore': row['settore'],
                'sasso': row['sasso'],
                'faccia': row['faccia'],
                'nome': row['nome'],
                'numero': row['numero'],
                'grado': row['grado'],
                'partenza': row['partenza'],
                'fa': row['fa'],
                'immagine': row['immagine'],
                'topos': row['topos'],
                'descrizione': row['descrizione'],
                'tag': row['tag']
            })

if __name__ == "__main__":
    update_csv(INPUT_CSV, OUTPUT_CSV)
    print(f"CSV aggiornato e salvato come '{OUTPUT_CSV}'")