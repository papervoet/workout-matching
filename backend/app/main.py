# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import matches as matches_router
from .db.base import init_db       # 🔹 DB 초기화 함수 가져오기

app = FastAPI(
    title="FitMatch Backend",
    version="0.2.0",
)

# CORS 설정 (지금은 개발 편하라고 전체 허용)
origins = [
    "*",  # Flutter 웹, 로컬 개발 등 다 허용
    # 나중에 실제 서비스 도메인만 남겨도 됨
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# 라우터 등록
app.include_router(matches_router.router)


# ✅ 서버 시작할 때 DB 테이블 자동 생성
@app.on_event("startup")
def on_startup():
    init_db()
