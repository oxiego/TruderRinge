from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    disag_start_number = Column(Integer, unique=True, index=True)
    category_class = Column(String, nullable=True)
    member_number = Column(String(8), unique=True, index=True, nullable=True)
    birth_date = Column(String, nullable=True)
    gender = Column(String(1), nullable=True)
    lg_participation = Column(Boolean, nullable=False, default=False)
    lp_participation = Column(Boolean, nullable=False, default=False)
    lg_fleisch_eligible = Column(Boolean, nullable=False, default=False)
    lp_fleisch_eligible = Column(Boolean, nullable=False, default=False)
    uses_aids = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    last_year_average_lg = Column(Float, nullable=True)
    last_year_average_lp = Column(Float, nullable=True)

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
    competition_date = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member")
