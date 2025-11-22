# backend/app/models/match.py

from sqlalchemy import Column, Integer, String, DateTime
from ..db.base import Base


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    # 1차 카테고리: 스포츠 종류
    sport = Column(String, nullable=False)        # "basketball" / "tennis" / "soccer"

    # 2차 카테고리: 농구 상세 타입
    game_type = Column(String, nullable=True)     # "pickup" / "scrimmage" / "guest" (농구일 때)

    game_time = Column(DateTime, nullable=False)  # 경기 일시
    level = Column(String, nullable=False)        # 실력
    place = Column(String, nullable=False)        # 장소
    note = Column(String, nullable=True)          # 기타 설명
