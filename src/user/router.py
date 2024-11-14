from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from ..auth import dependencies
from . import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix = "/users",
)

@router.post("/create", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already existed
    db_user = crud.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user, db=db)

@router.get(
    "/retrieve/{email}", 
    response_model=schemas.User,
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]), 
        Depends(dependencies.confirm_user_authorization)
    ])
def read_user(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(email=email, db=db)
    if not db_user: 
        raise HTTPException(status_code=404, detail="Target user does not exist")
    return db_user

@router.patch(
    "/update/{email}", 
    response_model=schemas.UserUpdate,     
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]), 
        Depends(dependencies.confirm_user_authorization)
    ])
def update_user(email: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(email=email, db=db)
    if not db_user:
        HTTPException(status_code=400, detail="Target user does not exist")
    return crud.update_user(email=email, user=user, db=db)

@router.delete(
    "/delete/{email}",     
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]), 
        Depends(dependencies.confirm_user_authorization)
    ])
def delete_user(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(email=email, db=db)
    if not db_user:
        HTTPException(status_code=400, detail="Target user does not exist")
    return crud.delete_user(email=email, db=db)

