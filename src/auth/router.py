from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from . import constants, schemas, service

router = APIRouter(
    prefix = "",
    tags = ["auth"],
)

@router.post("/token")
async def login_for_access_and_refresh_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    #authenticate user
    user = service.authenticate_user(entered_email=form_data.username, entered_password=form_data.password, db=db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    '''Create Access Token'''
    access_token_expire_duration = timedelta(weeks=constants.ACCESS_TOKEN_EXPIRE_WEEKS)
    access_token = service.create_access_token(
        payload = {"email": form_data.username, "scope": user.status},
        expires_delta = access_token_expire_duration
    )

    '''Create Refresh Token'''
    refresh_token_expire_duration = timedelta(weeks=constants.REFRESH_TOKEN_EXPIRE_WEEKS)
    refresh_token = service.create_refresh_token(
        payload = {"email": form_data.username, "scope": user.status},
        expires_delta = refresh_token_expire_duration
    )
    token = {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
        "token_type" : "bearer"
    }
    return schemas.Token(**token)
