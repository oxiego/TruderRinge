from datetime import date
from typing import BinaryIO, Literal
import os
import tempfile

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from app import models
from app.database import engine, get_db
from app.wmk_parser import WMKParser
from app.rule_engine import RuleEngine

models.Base.metadata.create_all(bind=engine)
BOOLEAN_DEFAULT_FALSE = "BOOLEAN NOT NULL DEFAULT 0"
with engine.begin() as connection:
    member_columns = {
        row[1] for row in connection.exec_driver_sql("PRAGMA table_info(members)")
    }
    migrations = {
        "member_number": "VARCHAR(8)",
        "birth_date": "VARCHAR",
        "gender": "VARCHAR(1)",
        "lg_participation": BOOLEAN_DEFAULT_FALSE,
        "lp_participation": BOOLEAN_DEFAULT_FALSE,
        "lg_fleisch_eligible": BOOLEAN_DEFAULT_FALSE,
        "lp_fleisch_eligible": BOOLEAN_DEFAULT_FALSE,
        "uses_aids": BOOLEAN_DEFAULT_FALSE,
        "active": "BOOLEAN NOT NULL DEFAULT 1",
        "last_year_average_lg": "FLOAT",
        "last_year_average_lp": "FLOAT",
    }
    for column, definition in migrations.items():
        if column not in member_columns:
            connection.exec_driver_sql(
                f"ALTER TABLE members ADD COLUMN {column} {definition}"
            )
    connection.exec_driver_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_members_member_number "
        "ON members (member_number)"
    )
    processed_shot_columns = {
        row[1] for row in connection.exec_driver_sql("PRAGMA table_info(processed_shots)")
    }
    if "competition_date" not in processed_shot_columns:
        connection.exec_driver_sql(
            "ALTER TABLE processed_shots ADD COLUMN competition_date VARCHAR"
        )
    connection.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_processed_shots_competition_date "
        "ON processed_shots (competition_date)"
    )

app = FastAPI(title="TruderRinge PoC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MemberCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    member_number: str | None = None
    birth_date: date
    gender: Literal["M", "W"]
    disag_start_number: int | None = Field(default=None, ge=1)
    lg_participation: bool = False
    lp_participation: bool = False
    lg_fleisch_eligible: bool = False
    lp_fleisch_eligible: bool = False
    uses_aids: bool = False
    active: bool = True
    last_year_average_lg: float | None = Field(default=None, ge=0)
    last_year_average_lp: float | None = Field(default=None, ge=0)

    @field_validator("first_name", "last_name")
    @classmethod
    def trim_names(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Vor- und Nachname dürfen nicht leer sein.")
        return value

    @field_validator("member_number")
    @classmethod
    def validate_member_number(cls, value: str | None) -> str | None:
        if value is not None and (len(value) != 8 or not value.isdigit()):
            raise ValueError("Die Mitgliedsnummer muss aus genau acht Ziffern bestehen.")
        return value


class MemberUpdate(MemberCreate):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    birth_date: date | None = None
    gender: Literal["M", "W"] | None = None


def serialize_member(member: models.Member) -> dict:
    return {
        "id": member.id,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "member_number": member.member_number,
        "birth_date": member.birth_date,
        "gender": member.gender,
        "disag_start_number": member.disag_start_number,
        "category_class": member.category_class,
        "lg_participation": member.lg_participation,
        "lp_participation": member.lp_participation,
        "lg_fleisch_eligible": member.lg_fleisch_eligible,
        "lp_fleisch_eligible": member.lp_fleisch_eligible,
        "uses_aids": member.uses_aids,
        "active": member.active,
        "last_year_average_lg": member.last_year_average_lg,
        "last_year_average_lp": member.last_year_average_lp,
    }


def next_temporary_member_number(db: Session) -> str:
    number = 99999999
    while db.query(models.Member.id).filter(
        models.Member.member_number == str(number)
    ).first():
        number -= 1
    if number < 0:
        raise HTTPException(
            status_code=409, detail="Es ist keine temporäre Mitgliedsnummer mehr verfügbar."
        )
    return str(number)


@app.get("/health")
def get_health():
    return {"status": "ok"}


@app.get("/members")
def get_members(db: Session = Depends(get_db)):
    members = db.query(models.Member).order_by(
        models.Member.last_name, models.Member.first_name, models.Member.id
    ).all()
    return [serialize_member(member) for member in members]


@app.post(
    "/members",
    status_code=201,
    responses={409: {"description": "Mitglieds- oder DISAG-Nummer bereits vergeben."}},
)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    member_number = payload.member_number or next_temporary_member_number(db)
    if db.query(models.Member.id).filter(
        models.Member.member_number == member_number
    ).first():
        raise HTTPException(status_code=409, detail="Die Mitgliedsnummer ist bereits vergeben.")
    if payload.disag_start_number is not None and db.query(models.Member.id).filter(
        models.Member.disag_start_number == payload.disag_start_number
    ).first():
        raise HTTPException(
            status_code=409, detail="Die DISAG-Startnummer ist bereits vergeben."
        )

    values = payload.model_dump(exclude={"member_number"})
    values["birth_date"] = payload.birth_date.isoformat()
    member = models.Member(**values, member_number=member_number)
    db.add(member)
    db.commit()
    db.refresh(member)
    return serialize_member(member)


@app.patch(
    "/members/{member_id}",
    responses={
        404: {"description": "Mitglied nicht gefunden."},
        409: {"description": "Mitglieds- oder DISAG-Nummer bereits vergeben."},
    },
)
def update_member(
    member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)
):
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if member is None:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden.")
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("member_number") is None:
        changes.pop("member_number", None)
    if "birth_date" in changes and changes["birth_date"] is not None:
        changes["birth_date"] = changes["birth_date"].isoformat()
    if changes.get("member_number") and db.query(models.Member.id).filter(
        models.Member.member_number == changes["member_number"],
        models.Member.id != member_id,
    ).first():
        raise HTTPException(status_code=409, detail="Die Mitgliedsnummer ist bereits vergeben.")
    if changes.get("disag_start_number") and db.query(models.Member.id).filter(
        models.Member.disag_start_number == changes["disag_start_number"],
        models.Member.id != member_id,
    ).first():
        raise HTTPException(
            status_code=409, detail="Die DISAG-Startnummer ist bereits vergeben."
        )
    for field, value in changes.items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return serialize_member(member)


def open_temp_wmk() -> tuple[str, BinaryIO]:
    temp_file = tempfile.NamedTemporaryFile(suffix=".wmk", delete=False)
    return temp_file.name, temp_file


def has_sqlite_header(path: str) -> bool:
    with open(path, "rb") as uploaded:
        return uploaded.read(16) == b"SQLite format 3\x00"


async def save_wmk_request(request: Request) -> str:
    path, temp_file = await run_in_threadpool(open_temp_wmk)
    size = 0
    try:
        async for chunk in request.stream():
            size += len(chunk)
            if size > 50 * 1024 * 1024:
                raise HTTPException(
                    status_code=413, detail="WMK-Dateien dürfen höchstens 50 MB groß sein."
                )
            await run_in_threadpool(temp_file.write, chunk)
        await run_in_threadpool(temp_file.close)
        if not await run_in_threadpool(has_sqlite_header, path):
            raise HTTPException(
                status_code=422, detail="Die ausgewählte Datei ist keine lesbare SQLite-WMK-Datei."
            )
        return path
    except Exception:
        if not temp_file.closed:
            await run_in_threadpool(temp_file.close)
        if os.path.exists(path):
            os.unlink(path)
        raise


@app.post(
    "/import/wmk/preview",
    responses={
        413: {"description": "WMK-Datei überschreitet die maximale Dateigröße."},
        422: {"description": "Ungültige oder nicht lesbare WMK-Datei."},
    },
)
async def preview_wmk_file(request: Request, db: Session = Depends(get_db)):
    path = await save_wmk_request(request)
    try:
        try:
            raw_shots = WMKParser(path).extract_results()
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail=f"WMK-Datei konnte nicht gelesen werden: {exc}"
            ) from exc
        if not raw_shots:
            raise HTTPException(
                status_code=422, detail="Die WMK-Datei enthält keine Wertungsschüsse."
            )
        start_numbers = sorted({shot["disag_start_number"] for shot in raw_shots})
        known_numbers = {
            number for (number,) in db.query(models.Member.disag_start_number).filter(
                models.Member.disag_start_number.in_(start_numbers)
            ).all()
        }
        return {
            "shot_count": len(raw_shots),
            "shooter_count": len(start_numbers),
            "unknown_start_numbers": [
                number for number in start_numbers if number not in known_numbers
            ],
        }
    finally:
        os.unlink(path)


@app.post(
    "/import/wmk",
    responses={
        413: {"description": "WMK-Datei überschreitet die maximale Dateigröße."},
        422: {"description": "Ungültige oder nicht lesbare WMK-Datei."},
    },
)
async def import_wmk_file(
    request: Request,
    competition_date: date,
    db: Session = Depends(get_db),
):
    path = await save_wmk_request(request)
    try:
        try:
            raw_shots = WMKParser(path).extract_results()
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail=f"WMK-Datei konnte nicht gelesen werden: {exc}"
            ) from exc
    finally:
        os.unlink(path)
    if not raw_shots:
        raise HTTPException(status_code=422, detail="Die WMK-Datei enthält keine Wertungsschüsse.")

    engine = RuleEngine(db)
    imported_count = 0
    rejected_shots = []

    for shot in raw_shots:
        try:
            engine.process_shot(
                disag_start_number=shot["disag_start_number"],
                shot_data=shot,
                competition_date=competition_date.isoformat()
            )
            imported_count += 1
        except ValueError as exc:
            rejected_shots.append({
                "disag_start_number": shot["disag_start_number"],
                "shot_number": shot["shot_number"],
                "reason": str(exc),
            })

    if rejected_shots:
        db.rollback()
        return {
            "status": "rejected",
            "imported_shots": 0,
            "rejected_shots": rejected_shots,
        }

    db.commit()
    return {
        "status": "success",
        "imported_shots": imported_count,
        "rejected_shots": rejected_shots,
    }

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
