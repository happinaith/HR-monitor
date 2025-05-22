from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from datetime import datetime, timezone
from src import models
import pandas as pd

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_vacancy(db: Session, vacancy_data: dict, team_lead_id: int):
    vacancy = models.Vacancy(
        title=vacancy_data["title"],
        created_by=team_lead_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy

def upload_resume(db: Session, resume_data: dict, hr_id: int):
    resume = models.Resume(
        candidate_name=resume_data["candidate_name"],
        source=resume_data.get("source"),
        vacancy_id=resume_data["vacancy_id"],
        current_stage=resume_data.get("current_stage", "открыта"),
        uploaded_by=hr_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume

def move_resume_stage(db: Session, resume_id: int, new_stage: str, hr_id: int):
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.uploaded_by == hr_id
    ).first()
    if not resume:
        return None
    resume.current_stage = new_stage
    stage_entry = models.ResumeStage(
        resume_id=resume_id,
        stage=new_stage,
        entered_at=datetime.now(timezone.utc)
    )
    db.add(stage_entry)
    db.commit()
    db.refresh(resume)
    return resume

def get_resumes(
    db: Session,
    user_id: int = None,
    stage: str = None,
    vacancy_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    sort_by: str = "created_at",
    sort_order: str = "asc"
):
    query = db.query(models.Resume)
    if user_id:
        query = query.filter(models.Resume.uploaded_by == user_id)
    if stage:
        query = query.filter(models.Resume.current_stage == stage)
    if vacancy_id:
        query = query.filter(models.Resume.vacancy_id == vacancy_id)
    if start_date:
        query = query.filter(models.Resume.created_at >= start_date)
    if end_date:
        query = query.filter(models.Resume.created_at <= end_date)
    if sort_by == "created_at":
        order = asc(models.Resume.created_at) if sort_order == "asc" else desc(models.Resume.created_at)
        query = query.order_by(order)
    elif sort_by == "sla_due":
        order = asc(models.Resume.created_at) if sort_order == "asc" else desc(models.Resume.created_at)
        query = query.order_by(order)
    return query.all()  # Должен возвращать список объектов Resume

def get_statistics(db: Session, user_id: int = None):
    query = db.query(models.Resume)
    if user_id:
        query = query.filter(models.Resume.uploaded_by == user_id)
    resumes = query.all()

    avg_stage_times = db.query(
        models.ResumeStage.stage,
        func.avg(
            func.extract('epoch', models.ResumeStage.entered_at)
        ).label('avg_seconds')
    )
    if user_id:
        avg_stage_times = avg_stage_times.join(models.Resume, models.Resume.id == models.ResumeStage.resume_id)\
            .filter(models.Resume.uploaded_by == user_id)
    avg_stage_times = avg_stage_times.group_by(models.ResumeStage.stage).all()

    resumes_per_stage = db.query(
        models.Resume.current_stage,
        func.count(models.Resume.id)
    )
    if user_id:
        resumes_per_stage = resumes_per_stage.filter(models.Resume.uploaded_by == user_id)
    resumes_per_stage = resumes_per_stage.group_by(models.Resume.current_stage).all()

    resumes_per_source = db.query(
        models.Resume.source,
        func.count(models.Resume.id)
    )
    if user_id:
        resumes_per_source = resumes_per_source.filter(models.Resume.uploaded_by == user_id)
    resumes_per_source = resumes_per_source.group_by(models.Resume.source).all()

    avg_candidates_per_vacancy = db.query(
        func.avg(
            db.query(models.Resume).filter(models.Resume.vacancy_id == models.Vacancy.id).count()
        )
    ).scalar()

    sla_violations_count = 0

    # Преобразование кортежей в DataFrame и далее в список словарей
    avg_stage_times_df = pd.DataFrame(avg_stage_times, columns=["stage", "avg_seconds"])
    resumes_per_stage_df = pd.DataFrame(resumes_per_stage, columns=["stage", "count"])
    resumes_per_source_df = pd.DataFrame(resumes_per_source, columns=["source", "count"])

    return {
        "avg_stage_times": avg_stage_times_df.to_dict(orient="records"),
        "resumes_per_stage": resumes_per_stage_df.to_dict(orient="records"),
        "resumes_per_source": resumes_per_source_df.to_dict(orient="records"),
        "avg_candidates_per_vacancy": avg_candidates_per_vacancy,
        "sla_violations": sla_violations_count
    }

def get_sla_settings(db: Session, team_lead_id: int):
    return db.query(models.SLASettings).filter(models.SLASettings.set_by == team_lead_id).all()

def set_sla_settings(db: Session, sla_data: dict, team_lead_id: int):
    for stage, max_days in sla_data.items():
        sla = db.query(models.SLASettings).filter(
            models.SLASettings.stage == stage
        ).first()
        if sla:
            sla.max_days = max_days
            sla.set_by = team_lead_id
            sla.set_at = datetime.now(timezone.utc)
        else:
            sla = models.SLASettings(
                stage=stage,
                max_days=max_days,
                set_by=team_lead_id,
                set_at=datetime.now(timezone.utc)
            )
            db.add(sla)
    db.commit()
    return get_sla_settings(db, team_lead_id)

def create_user(db: Session, user_data: dict):
    user = models.User(
        username=user_data["username"],
        password_hash=user_data["password_hash"],
        role=user_data["role"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user  # Должен возвращать объект User