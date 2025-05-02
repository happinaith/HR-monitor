from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src import crud, models, database, auth
from src.database import Base, engine

app = FastAPI()

from src.models import user, vacancy, resume, resume_stage, sla_settings

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/resumes/")
def get_resumes(stage: str = None, vacancy_id: int = None, start_date: datetime = None,end_date: datetime = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    resumes = crud.get_resumes(db, current_user.id, stage, vacancy_id, start_date, end_date)
    return resumes

@app.get("/statistics/")
def get_statistics(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    statistics = crud.get_statistics(db, current_user)
    return statistics