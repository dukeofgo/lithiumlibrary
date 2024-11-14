from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .books import router as books_router
from .database import Base, engine
from .users import router as users_router

Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(users_router.router, prefix="/api")
app.include_router(books_router.router, prefix="/api")
app.include_router(auth_router.router, prefix="/api")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)