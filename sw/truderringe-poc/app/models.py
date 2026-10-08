from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
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
