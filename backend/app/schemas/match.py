# backend/app/schemas/match.py

from datetime import datetime
from pydantic import BaseModel


class MatchBase(BaseModel):
    sport: str              # "basketball" / "tennis" / "soccer"
    game_type: str | None   # 농구일 때: "pickup" / "scrimmage" / "guest"
    game_time: datetime     # 경기 일시
    level: str              # 실력
    place: str              # 장소
    note: str | None = None # 기타 설명


class MatchCreate(MatchBase):
    """매칭 생성용 스키마"""
    pass


class MatchUpdate(MatchBase):
    """매칭 수정용 스키마"""
    pass


class Match(MatchBase):
    """응답용 스키마 (id 포함)"""
    id: int

    class Config:
        from_attributes = True
