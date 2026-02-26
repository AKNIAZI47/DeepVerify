"""Export service for analysis results."""
import csv
import json
from io import StringIO
from typing import List, Dict
from datetime import datetime

class ExportService:
    @staticmethod
    def export_to_csv(data: List[Dict]) -> str:
        if not data:
            return ""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    @staticmethod
    def export_to_json(data: List[Dict]) -> str:
        return json.dumps(data, indent=2, default=str)

def get_export_service() -> ExportService:
    return ExportService()
