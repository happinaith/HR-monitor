from fastapi import FastAPI, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from datetime import datetime
from src import crud, models, database, auth
from src.database import Base, engine
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI()

from src.models import user, vacancy, resume, resume_stage, sla_settings

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_role(user: models.User, allowed_roles: List[str]):
    if user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not enough permissions")

class VacancyCreate(BaseModel):
    title: str

class ResumeCreate(BaseModel):
    candidate_name: str
    source: Optional[str] = None
    vacancy_id: int
    current_stage: Optional[str] = "открыта"

class SLASettingsUpdate(BaseModel):
    settings: dict[str, int]

class ResumeStageUpdate(BaseModel):
    new_stage: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str  #hr или team_lead_hr

@app.post("/vacancies/")
def create_vacancy(
    vacancy_data: VacancyCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    check_role(current_user, ["team_lead_hr"])
    return crud.create_vacancy(db, vacancy_data.dict(), current_user.id)

@app.post("/resumes/")
def upload_resume(
    resume_data: ResumeCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    check_role(current_user, ["hr"])
    return crud.upload_resume(db, resume_data.dict(), current_user.id)

@app.patch("/resumes/{resume_id}/stage/")
def move_resume_stage(
    resume_id: int,
    stage_update: ResumeStageUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    check_role(current_user, ["hr"])
    return crud.move_resume_stage(db, resume_id, stage_update.new_stage, current_user.id)

@app.get("/resumes/")
def get_resumes(
    stage: Optional[str] = Query(None, description="Фильтр по стадии"),
    vacancy_id: Optional[int] = Query(None, description="Фильтр по вакансии"),
    start_date: Optional[datetime] = Query(None, description="Дата от"),
    end_date: Optional[datetime] = Query(None, description="Дата до"),
    sort_by: Optional[str] = Query("created_at", enum=["created_at", "sla_due"], description="Сортировка"),
    sort_order: Optional[str] = Query("asc", enum=["asc", "desc"], description="Порядок сортировки"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == "hr":
        user_id = current_user.id
    elif current_user.role == "team_lead_hr":
        user_id = None
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    resumes = crud.get_resumes(
        db, user_id, stage, vacancy_id, start_date, end_date,
        sort_by=sort_by, sort_order=sort_order
    )
    return resumes

@app.get("/statistics/")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    if current_user.role == "hr":
        user_id = current_user.id
    elif current_user.role == "team_lead_hr":
        user_id = None
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    statistics = crud.get_statistics(db, user_id)
    return statistics

@app.get("/sla-settings/")
def get_sla_settings(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    check_role(current_user, ["team_lead_hr"])
    return crud.get_sla_settings(db, current_user.id)

@app.post("/sla-settings/")
def set_sla_settings(
    sla_data: dict = Body(..., example={"открыта": 2, "изучена": 3}),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    check_role(current_user, ["team_lead_hr"])
    return crud.set_sla_settings(db, sla_data, current_user.id)

@app.post("/users/")
def create_user(
    user_data: UserCreate = Body(...),
    db: Session = Depends(get_db)
):
    user_dict = {
        "username": user_data.username,
        "password_hash": user_data.password,
        "role": user_data.role
    }
    return crud.create_user(db, user_dict)