from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # <-- DIESE ZEILE FEHLT
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],  # Angular Dev-Server
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt POST, GET, OPTIONS etc.
    allow_headers=["*"],
)

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
