from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime, timezone

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    current_stage = Column(String, nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    vacancy = relationship("Vacancy")
    uploader = relationship("User")