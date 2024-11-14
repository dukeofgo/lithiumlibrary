
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from datetime import datetime, timezone

from ..auth import config, exceptions
from ..user import schemas, crud

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/token"
)

def authorize_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    try:
        payload = jwt.decode(token, config.SECRET_KEY, config.JWT_ALGORITHM)
        payload_email = payload.get("email")
        payload_scope = payload.get("scope")
        payload_expire = payload.get("exp")

        """JWT automatically convert datetime to timestamp when encode data,
        it is necessary to convert timestamp type back to datetime type after decoding payload"""
        payload_expire_datetime = datetime.fromtimestamp(payload_expire, tz=(timezone.utc))

        user_token_data = schemas.JWTTokenData(email=payload_email, scope=payload_scope, expire_date=payload_expire_datetime)

    except (InvalidTokenError, ValidationError):
        raise exceptions.credentials_exception("Could not validate credentials1", authenticate_value)

    #verifying permission
    if user_token_data.scope not in security_scopes.scopes:
        raise exceptions.credentials_exception("User doesn't have enough privilege", authenticate_value)
        
#verifying both identity and role
#check either user is logged in as the user or user is admin or superuser
def confirm_user_authorization(email: str, token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, config.JWT_ALGORITHM)
        payload_email = payload.get("email")
        payload_scope = payload.get("scope")
        payload_expire = payload.get("exp")

        """JWT automatically convert datetime to timestamp when encode data,
        it is necessary to convert timestamp type back to datetime type after decoding payload"""
        payload_expire_datetime = datetime.fromtimestamp(payload_expire, tz=(timezone.utc))

        user_token_data = schemas.JWTTokenData(email=payload_email, scope=payload_scope, expire_date=payload_expire_datetime)
        
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=401, detail="Could not validate credentials2")

    # if current user's email doesn't match the email of the requested user, and current user's scope isn't admin or superuser
    if email != user_token_data.email and user_token_data.scope not in ["admin", "superuser"]:
        raise HTTPException(status_code=401, detail="Could not validate credentials3")

