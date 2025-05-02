from sqlalchemy.orm import Session
from datetime import datetime
from src import models

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_resumes(db: Session, user_id: int, stage: str = None, vacancy_id: int = None, start_date: datetime = None, end_date: datetime = None):
    query = db.query(models.Resume).filter(models.Resume.owner_id == user_id)
    
    if stage:
        query = query.filter(models.Resume.current_stage == stage)
    if vacancy_id:
        query = query.filter(models.Resume.id == vacancy_id)
    if start_date:
        query = query.filter(models.Resume.created_at >= start_date)
    if end_date:
        query = query.filter(models.Resume.created_at <= end_date)
    
    return query.all()

def get_statistics(db: Session, user_id: int):
    resumes_per_stage = db.query(models.Resume.stage, db.func.count(models.Resume.id)).group_by(models.Resume.stage).all()
    resumes_per_source = db.query(models.Resume.source, db.func.count(models.Resume.id)).group_by(models.Resume.source).all()

    if user_id.role == 'team_lead_hr':
        hr_resumes = db.query(models.Resume).filter(models.Resume.uploaded_by != user_id).all()
    else:
        hr_resumes = db.query(models.Resume).filter(models.Resume.uploaded_by == user_id).all()

    return {
        "resumes_per_stage": resumes_per_stage,
        "resumes_per_source": resumes_per_source,
        "total_resumes": len(hr_resumes)
    }