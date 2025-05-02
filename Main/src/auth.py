from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import main, crud

def get_current_user(db: Session = Depends(main.get_db)):
    user = crud.get_user_by_id(db, user_id=1)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user