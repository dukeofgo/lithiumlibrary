import os

HASH_ALGORITHM = os.environ.get("HASH_ALGORITHM")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
SECRET_KEY = os.environ.get("SECRET_KEY")