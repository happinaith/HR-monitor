from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime, timezone

class SLASetting(Base):
    __tablename__ = "sla_settings"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(String, unique=True, nullable=False)
    max_days = Column(Integer, nullable=False)
    set_by = Column(Integer, ForeignKey("users.id"))
    set_at = Column(DateTime, default=datetime.now(timezone.utc))

    setter = relationship("User")