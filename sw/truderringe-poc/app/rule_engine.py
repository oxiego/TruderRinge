from sqlalchemy.orm import Session
from app.models import Member, ProcessedShot

class RuleEngine:
    def __init__(self, db: Session):
        self.db = db

    def process_shot(self, disag_start_number: int, shot_data: dict, competition_date: str) -> ProcessedShot:
        member = self.db.query(Member).filter(Member.disag_start_number == disag_start_number).first()
        if not member:
            raise ValueError(f"Schütze {disag_start_number} nicht gefunden.")

        processed_shot = ProcessedShot(
            member_id=member.id,
            shot_number=shot_data["shot_number"],
            series_number=None,
            ring_value=shot_data["ring_value"],
            tenth_value=shot_data["tenth_value"],
            teiler=shot_data["teiler"],
            target_category="UNGEWERTET",
            competition_date=competition_date
        )
        self.db.add(processed_shot)
        return processed_shot
