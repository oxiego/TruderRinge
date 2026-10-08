import os
import zipfile

# Dateistruktur und Inhalte
files = {
    "truderringe-poc/requirements.txt": """fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
""",
    "truderringe-poc/app/__init__.py": "",
    "truderringe-poc/app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./truderringe.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "truderringe-poc/app/models.py": """from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    disag_start_number = Column(Integer, unique=True, index=True)
    category_class = Column(String)

class ClassNightStatus(Base):
    __tablename__ = "class_night_status"

    id = Column(Integer, primary_key=True, index=True)
    competition_date = Column(String, index=True)
    category_class = Column(String, index=True)
    fleischpreis_active = Column(Boolean, default=True)
    remaining_prizes = Column(Integer, default=5)

class ProcessedShot(Base):
    __tablename__ = "processed_shots"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    shot_number = Column(Integer)
    series_number = Column(Integer)
    ring_value = Column(Integer)
    tenth_value = Column(Float)
    teiler = Column(Float)
    target_category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member")
""",
    "truderringe-poc/app/wmk_parser.py": """import sqlite3
from typing import List, Dict, Any

class WMKParser:
    def __init__(self, wmk_file_path: str):
        self.wmk_file_path = wmk_file_path

    def extract_results(self) -> List[Dict[str, Any]]:
        results = []
        try:
            conn = sqlite3.connect(f"file:{self.wmk_file_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            query = \"\"\"
                SELECT 
                    s.StartNr, s.SchussNr, s.Ringe, s.Zehntel, s.Teiler, s.IsProbe
                FROM SchuetzenSchuesse s
                WHERE s.IsProbe = 0
                ORDER BY s.StartNr, s.SchussNr
            \"\"\"
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
""",
    "truderringe-poc/app/rule_engine.py": """from sqlalchemy.orm import Session
from app.models import Member, ClassNightStatus, ProcessedShot

class RuleEngine:
    def __init__(self, db: Session):
        self.db = db

    def process_shot(self, disag_start_number: int, shot_data: dict, competition_date: str) -> ProcessedShot:
        member = self.db.query(Member).filter(Member.disag_start_number == disag_start_number).first()
        if not member:
            raise ValueError(f"Schütze {disag_start_number} nicht gefunden.")

        status = self.db.query(ClassNightStatus).filter(
            ClassNightStatus.competition_date == competition_date,
            ClassNightStatus.category_class == member.category_class
        ).first()

        if not status:
            status = ClassNightStatus(
                competition_date=competition_date,
                category_class=member.category_class,
                fleischpreis_active=True,
                remaining_prizes=5
            )
            self.db.add(status)
            self.db.commit()

        target_category = "POKAL"
        shot_num = shot_data["shot_number"]

        if 1 <= shot_num <= 20:
            if status.fleischpreis_active and status.remaining_prizes > 0:
                target_category = "FLEISCHPREIS"
            else:
                target_category = "POKAL"
        else:
            target_category = "POKAL"

        series_num = ((shot_num - 1) // 10) + 1

        processed_shot = ProcessedShot(
            member_id=member.id,
            shot_number=shot_num,
            series_number=series_num,
            ring_value=shot_data["ring_value"],
            tenth_value=shot_data["tenth_value"],
            teiler=shot_data["teiler"],
            target_category=target_category
        )
        self.db.add(processed_shot)
        self.db.commit()
        return processed_shot
""",
    "truderringe-poc/app/main.py": """from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app import models
from app.database import engine, get_db
from app.wmk_parser import WMKParser
from app.rule_engine import RuleEngine
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TruderRinge PoC")

@app.on_event("startup")
def startup_populate_test_data():
    db = next(get_db())
    if not db.query(models.Member).first():
        m1 = models.Member(first_name="Max", last_name="Mustermann", disag_start_number=101, category_class="PISTOLE")
        m2 = models.Member(first_name="Erika", last_name="Musterfrau", disag_start_number=102, category_class="GEWEHR_HERREN")
        db.add_all([m1, m2])
        db.commit()

@app.post("/import/wmk")
def import_wmk_file(wmk_path: str = "data/sample.wmk", competition_date: str = "2026-10-08", db: Session = Depends(get_db)):
    parser = WMKParser(wmk_path)
    raw_shots = parser.extract_results()
    engine = RuleEngine(db)
    imported_count = 0

    for shot in raw_shots:
        try:
            engine.process_shot(
                disag_start_number=shot["disag_start_number"],
                shot_data=shot,
                competition_date=competition_date
            )
            imported_count += 1
        except ValueError:
            continue

    return {"status": "success", "imported_shots": imported_count}

@app.get("/results/fleischpreis")
def get_fleischpreis_leaderboard(db: Session = Depends(get_db)):
    shots = db.query(models.ProcessedShot).filter(
        models.ProcessedShot.target_category == "FLEISCHPREIS"
    ).order_by(models.ProcessedShot.teiler.asc()).all()

    return [{
        "member_name": f"{s.member.first_name} {s.member.last_name}",
        "class": s.member.category_class,
        "teiler": s.teiler,
        "shot_number": s.shot_number
    } for s in shots]

@app.get("/results/pokal")
def get_pokal_leaderboard(db: Session = Depends(get_db)):
    shots = db.query(models.ProcessedShot).filter(
        models.ProcessedShot.target_category == "POKAL"
    ).all()

    results = {}
    for s in shots:
        mid = s.member_id
        if mid not in results:
            results[mid] = {
                "name": f"{s.member.first_name} {s.member.last_name}",
                "class": s.member.category_class,
                "total_rings": 0,
                "total_tenths": 0.0,
                "shot_count": 0
            }
        results[mid]["total_rings"] += s.ring_value
        results[mid]["total_tenths"] += round(s.tenth_value, 1)
        results[mid]["shot_count"] += 1

    return list(results.values())

if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")
""",
    "truderringe-poc/frontend/index.html": """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TruderRinge - Schießleiter Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen" x-data="truderRingeApp()" x-init="fetchData()">

    <!-- Header -->
    <header class="bg-slate-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center shadow-lg">
        <div class="flex items-center space-x-3">
            <div class="bg-emerald-600 text-white p-2 rounded-lg font-bold text-xl">TR</div>
            <div>
                <h1 class="text-xl font-bold tracking-wide">TruderRinge</h1>
                <p class="text-xs text-slate-400">SG Gemütlichkeit Trudering e.V.</p>
            </div>
        </div>
        <button @click="triggerImport()" :disabled="loading" class="bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-4 py-2 rounded-lg shadow flex items-center space-x-2 transition">
            <span x-show="!loading">📥 WM-Shot .wmk Import auslösen</span>
            <span x-show="loading" class="animate-pulse">Importiere Daten...</span>
        </button>
    </header>

    <!-- Main Content -->
    <main class="p-6 max-w-7xl mx-auto space-y-6">

        <div x-show="statusMessage" x-text="statusMessage" class="bg-emerald-900/50 border border-emerald-500 text-emerald-200 px-4 py-3 rounded-lg text-sm"></div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

            <!-- Fleischpreis Leaderboard -->
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-amber-400 flex items-center space-x-2">
                        <span>🥩</span>
                        <span>Fleischpreis Wertung (Best-Teiler)</span>
                    </h2>
                    <span class="text-xs bg-slate-700 px-2.5 py-1 rounded-full text-slate-300">Schuss 1–20</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-slate-700 text-xs text-slate-400 uppercase">
                                <th class="pb-2">Rang</th>
                                <th class="pb-2">Schütze</th>
                                <th class="pb-2">Klasse</th>
                                <th class="pb-2 text-right">Teiler</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-700/50 text-sm">
                            <template x-for="(row, index) in fleischpreisList" :key="index">
                                <tr class="hover:bg-slate-700/30 transition">
                                    <td class="py-2.5 font-bold" x-text="index + 1"></td>
                                    <td class="py-2.5 font-medium text-slate-200" x-text="row.member_name"></td>
                                    <td class="py-2.5">
                                        <span class="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300" x-text="row.class"></span>
                                    </td>
                                    <td class="py-2.5 text-right font-mono font-bold text-amber-400" x-text="row.teiler.toFixed(1)"></td>
                                </tr>
                            </template>
                            <tr x-show="fleischpreisList.length === 0">
                                <td colspan="4" class="py-4 text-center text-slate-500 text-xs">Noch keine Daten importiert. Klicke oben auf Import.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Pokal / Jahrestabelle -->
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-sky-400 flex items-center space-x-2">
                        <span>🏆</span>
                        <span>Pokal / Jahrestabelle</span>
                    </h2>
                    <span class="text-xs bg-slate-700 px-2.5 py-1 rounded-full text-slate-300">Ringe & Zehntel</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-slate-700 text-xs text-slate-400 uppercase">
                                <th class="pb-2">Schütze</th>
                                <th class="pb-2">Klasse</th>
                                <th class="pb-2 text-center">Schüsse</th>
                                <th class="pb-2 text-right">Ringe (Zehntel)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-700/50 text-sm">
                            <template x-for="(row, index) in pokalList" :key="index">
                                <tr class="hover:bg-slate-700/30 transition">
                                    <td class="py-2.5 font-medium text-slate-200" x-text="row.name"></td>
                                    <td class="py-2.5">
                                        <span class="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300" x-text="row.class"></span>
                                    </td>
                                    <td class="py-2.5 text-center text-slate-400" x-text="row.shot_count"></td>
                                    <td class="py-2.5 text-right font-mono font-bold text-sky-400">
                                        <span x-text="row.total_rings"></span>
                                        <span class="text-xs text-sky-300 font-normal" x-text="`(${row.total_tenths.toFixed(1)})`"></span>
                                    </td>
                                </tr>
                            </template>
                            <tr x-show="pokalList.length === 0">
                                <td colspan="4" class="py-4 text-center text-slate-500 text-xs">Noch keine Daten importiert. Klicke oben auf Import.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </main>

    <script>
        function truderRingeApp() {
            return {
                fleischpreisList: [],
                pokalList: [],
                loading: false,
                statusMessage: "",
                async fetchData() {
                    try {
                        const fpRes = await fetch("/results/fleischpreis");
                        this.fleischpreisList = await fpRes.json();

                        const pRes = await fetch("/results/pokal");
                        this.pokalList = await pRes.json();
                    } catch (e) {
                        console.error("Fehler beim Laden:", e);
                    }
                },
                async triggerImport() {
                    this.loading = true;
                    this.statusMessage = "";
                    try {
                        const res = await fetch("/import/wmk", { method: "POST" });
                        const data = await res.json();
                        this.statusMessage = "✅ Import erfolgreich: " + data.imported_shots + " Schüsse verarbeitet und nach Sequenzierungs-Regeln verteilt.";
                        await this.fetchData();
                    } catch (e) {
                        this.statusMessage = "❌ Fehler beim Importieren der Daten.";
                    } finally {
                        this.loading = false;
                    }
                }
            }
        }
    </script>
</body>
</html>
"""
}

# Ordner anlegen & Dateien erzeugen
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ZIP-Archiv bauen
with zipfile.ZipFile("truderringe-poc-full.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
    for path in files.keys():
        zipf.write(path)

print("ZIP-Datei erfolgreich erstellt: truderringe-poc-full.zip")
