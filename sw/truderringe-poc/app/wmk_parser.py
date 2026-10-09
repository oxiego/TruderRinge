import sqlite3
from contextlib import closing
from typing import List, Dict, Any

class WMKParser:
    def __init__(self, wmk_file_path: str):
        self.wmk_file_path = wmk_file_path

    def extract_results(self) -> List[Dict[str, Any]]:
        with closing(sqlite3.connect(f"file:{self.wmk_file_path}?mode=ro", uri=True)) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    s.StartNr, s.SchussNr, s.Ringe, s.Zehntel, s.Teiler, s.IsProbe
                FROM SchuetzenSchuesse s
                WHERE s.IsProbe = 0
                ORDER BY s.StartNr, s.SchussNr
            """
            cursor.execute(query)
            rows = cursor.fetchall()

        return [{
                    "disag_start_number": row[0],
                    "shot_number": row[1],
                    "ring_value": row[2],
                    "tenth_value": row[3],
                    "teiler": row[4],
                    "is_practice": bool(row[5])
                } for row in rows]
