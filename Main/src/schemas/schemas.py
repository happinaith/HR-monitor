from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel

class VacancyCreate(BaseModel):
    title: str

class ResumeCreate(BaseModel):
    candidate_name: str
    source: Optional[str] = None
    vacancy_id: int
    current_stage: Optional[str] = "открыта"

class SLASettingsUpdate(BaseModel):
    settings: Dict[str, int]

class ResumeStageUpdate(BaseModel):
    new_stage: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # hr или team_lead_hr

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        orm_mode = True

class VacancyOut(BaseModel):
    id: int
    title: str
    created_by: int
    created_at: datetime
    class Config:
        orm_mode = True

class ResumeOut(BaseModel):
    id: int
    candidate_name: str
    source: Optional[str]
    created_at: datetime
    current_stage: str
    vacancy_id: int
    uploaded_by: int
    class Config:
        orm_mode = True
