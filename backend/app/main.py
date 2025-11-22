# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import matches
from .db.session import engine
from .db.base import Base

app = FastAPI(
    title="FitMatch Backend",
    version="0.1.0",
)

# ✅ CORS 설정 – 일단 개발 단계라 전체 다 열어버리자
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 개발용: 어디서든 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(matches.router, prefix="/matches", tags=["Matches"])
