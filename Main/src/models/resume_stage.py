from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime, timezone

class ResumeStage(Base):
    __tablename__ = "resume_stages"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    stage = Column(String, nullable=False)
    entered_at = Column(DateTime, default=datetime.now(timezone.utc))

    resume = relationship("Resume")