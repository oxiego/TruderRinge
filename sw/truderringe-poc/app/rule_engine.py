from sqlalchemy.orm import Session
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
