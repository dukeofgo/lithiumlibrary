from fastapi import HTTPException, status

def credentials_exception(error_detail: str, authenticate_value: str):
    return HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = error_detail,
        headers = {"WWW-Authenticate": authenticate_value})