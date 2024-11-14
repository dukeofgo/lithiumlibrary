from datetime import datetime, timezone, timedelta

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..user import crud
from . import config

#initializes a CryptContext for hashing (passlib)
hash_context = CryptContext(schemes=[config.HASH_ALGORITHM])

#hash password with passlib
def hash_password(password: str):
    return hash_context.hash(password)

def verify_hashed_password(password: str, hashed_password: str):
    return hash_context.verify(password, hashed_password)

def authenticate_user(db: Session, entered_email: str, entered_password: str):
    db_user = crud.get_user_by_email(db=db, email=entered_email)
    if not db_user:
        return False
    if not verify_hashed_password(entered_password, db_user.hashed_password):
        return False
    return db_user
    
def create_access_token(payload: dict, expires_delta: timedelta = timedelta(days=1)):
    expire_date = datetime.now(tz=timezone.utc) + expires_delta
    payload.update({"exp": expire_date})
    
    encoded_jwt = jwt.encode(payload, config.SECRET_KEY, config.JWT_ALGORITHM)

    return encoded_jwt

def create_refresh_token(payload: dict, expires_delta: timedelta = timedelta(weeks=26)):
    expire_date = datetime.now(tz=timezone.utc) + expires_delta
    payload.update({"exp": expire_date})

    encoded_jwt = jwt.encode(payload, config.SECRET_KEY, config.JWT_ALGORITHM)

    return encoded_jwt