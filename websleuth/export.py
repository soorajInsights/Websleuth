import csv
import json
from pathlib import Path

class DataExporter:
    def __init__(self, data=None, filename="scraped_data.json"):
        """
        Optional immediate export on init if data is provided.
        """
        self.export_path = Path(".")
        self.filename = Path(filename).stem  # Get filename without extension

        self.export_path.mkdir(parents=True, exist_ok=True)

        if data:
            if filename.endswith(".json"):
                self.JSONExporter(data)
            elif filename.endswith(".csv"):
                self.CSVExporter(data)

    def CSVExporter(self, data):
        if not data:
            print("No data to export to CSV.")
            return

        keys = data[0].keys()
        file_path = self.export_path / f"{self.filename}.csv"

        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        print(f"[✓] Data exported to CSV: {file_path}")

    def JSONExporter(self, data):
        file_path = self.export_path / f"{self.filename}.json"

        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[✓] Data exported to JSON: {file_path}")
