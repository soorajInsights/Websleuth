import csv
import json
import asyncio
from pathlib import Path
from openpyxl import Workbook
import aiofiles

class BaseExporter:
    def __init__(self, export_path="."):
        self.export_path = Path(export_path)
        self.export_path.mkdir(parents=True, exist_ok=True)

    def _get_file_info(self, filename):
        if not filename:
            filename = "scraped_data.json"

        path = Path(filename)
        name = path.stem
        ext = path.suffix.lower() or ".json"
        full_path = self.export_path / f"{name}{ext}"
        return name, ext, full_path

class DataExporter(BaseExporter):
    def export(self, data, filename=None):
        name, ext, full_path = self._get_file_info(filename)

        try:
            if ext == ".json":
                return self._export_json(data, full_path)
            elif ext == ".csv":
                return self._export_csv(data, full_path)
            elif ext == ".xlsx":
                return self._export_excel(data, full_path)
            else:
                return self._export_json(data, self.export_path / f"{name}.json")
        except Exception as e:
            print(f"[✘] Error during export: {e}")

    def _export_json(self, data, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[✓] Data exported to JSON: {path}")
        except IOError as e:
            print(f"[✘] IOError while exporting JSON: {e}")
        except Exception as e:
            print(f"[✘] Unexpected error during JSON export: {e}")

    def _export_csv(self, data, path):
        if not data:
            print("No data to export to CSV.")
            return
        try:
            keys = data[0].keys()
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            print(f"[✓] Data exported to CSV: {path}")
        except IOError as e:
            print(f"[✘] IOError while exporting CSV: {e}")
        except Exception as e:
            print(f"[✘] Unexpected error during CSV export: {e}")

    def _export_excel(self, data, path):
        if not data:
            print("No data to export to Excel.")
            return
        try:
            wb = Workbook()
            ws = wb.active
            headers = list(data[0].keys())
            ws.append(headers)
            for row in data:
                ws.append([row.get(h, "") for h in headers])
            wb.save(path)
            print(f"[✓] Data exported to Excel: {path}")
        except Exception as e:
            print(f"[✘] Unexpected error during Excel export: {e}")

class AsyncDataExporter(BaseExporter):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def export(self, data, filename=None):
        name, ext, full_path = self._get_file_info(filename)

        try:
            if ext == ".json":
                await self._export_json(data, full_path)
            elif ext == ".csv":
                await self._export_csv(data, full_path)
            elif ext == ".xlsx":
                await self._export_excel(data, full_path)
            else:
                await self._export_json(data, self.export_path / f"{name}.json")
        except Exception as e:
            print(f"[✘] Error during export: {e}")

    async def _export_json(self, data, path):
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
                await f.write(json_str)
            print(f"[✓] Data exported to JSON: {path}")
        except IOError as e:
            print(f"[✘] IOError while exporting JSON asynchronously: {e}")
        except Exception as e:
            print(f"[✘] Unexpected error during async JSON export: {e}")

    async def _export_csv(self, data, path):
        if not data:
            print("No data to export to CSV.")
            return
        try:
            keys = data[0].keys()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._write_csv_sync, data, keys, path)
        except Exception as e:
            print(f"[✘] Error while exporting CSV asynchronously: {e}")

    async def _export_excel(self, data, path):
        if not data:
            print("No data to export to Excel.")
            return
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._write_excel_sync, data, path)
        except Exception as e:
            print(f"[✘] Error while exporting Excel asynchronously: {e}")

    def _write_csv_sync(self, data, keys, path):
        try:
            with open(path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            print(f"[✓] Data exported to CSV: {path}")
        except IOError as e:
            print(f"[✘] IOError while exporting CSV synchronously: {e}")
        except Exception as e:
            print(f"[✘] Unexpected error during CSV synchronous export: {e}")

    def _write_excel_sync(self, data, path):
        try:
            wb = Workbook()
            ws = wb.active
            headers = list(data[0].keys())
            ws.append(headers)
            for row in data:
                ws.append([row.get(h, "") for h in headers])
            wb.save(path)
            print(f"[✓] Data exported to Excel: {path}")
        except Exception as e:
            print(f"[✘] Unexpected error during Excel synchronous export: {e}")
