import csv
import json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "public" / "data"
JSON_DIR = BASE_DIR / "public" / "data_json"
csv_files = sorted(CSV_DIR.glob('*.csv'))
for csv_path in csv_files:
    with csv_path.open('r', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = [
            row
            for row in reader
            if any(value.strip() for value in row.values())
        ]
        json_path = JSON_DIR / (csv_path.stem + '.json')
        with json_path.open('w', encoding='utf-8') as json_file:
            json.dump(rows, json_file, ensure_ascii=False, indent=2)
        print(csv_path.name,len(rows))
    