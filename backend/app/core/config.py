# backend/app/core/config.py

import os

# 환경변수에 DATABASE_URL이 있으면 그걸 쓰고, 없으면 SQLite 파일 사용
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
