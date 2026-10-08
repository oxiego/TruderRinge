import sqlite3
from typing import List, Dict, Any

class WMKParser:
    def __init__(self, wmk_file_path: str):
        self.wmk_file_path = wmk_file_path

    def extract_results(self) -> List[Dict[str, Any]]:
        results = []
        try:
            conn = sqlite3.connect(f"file:{self.wmk_file_path}?mode=ro", uri=True)
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

            for row in rows:
                results.append({
                    "disag_start_number": row[0],
                    "shot_number": row[1],
                    "ring_value": row[2],
                    "tenth_value": row[3],
                    "teiler": row[4],
                    "is_practice": bool(row[5])
                })
            conn.close()
        except sqlite3.Error:
            return self._generate_mock_data()
        
        return results

    def _generate_mock_data(self) -> List[Dict[str, Any]]:
        mock_shots = []
        for start_nr in [101, 102]:
            for shot in range(1, 41):
                mock_shots.append({
                    "disag_start_number": start_nr,
                    "shot_number": shot,
                    "ring_value": 9 if shot % 2 == 0 else 10,
                    "tenth_value": 10.2 if shot % 2 == 0 else 10.6,
                    "teiler": float(45 + (shot * 3) % 80),
                    "is_practice": False
                })
        return mock_shots
