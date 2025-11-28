# backend/app/schemas/match.py

from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# 🔹 공통 필드: 생성/수정/응답 모두에서 쓰는 기본 구조
class MatchBase(BaseModel):
    title: str                           # 매칭 제목
    description: Optional[str] = None    # 설명 (선택)
    sport: Optional[str] = None          # 종목 (예: 농구, 풋살, 롤) - 선택
    location: str                        # 장소

    date: date                           # 날짜 (2025-11-30 같은 형식)
    start_time: time                     # 시작 시간
    end_time: Optional[time] = None      # 종료 시간 (선택)

    max_people: int                      # 최대 인원


# 🔹 생성용: POST /matches 에서 사용하는 요청 바디
class MatchCreate(MatchBase):
    # 지금은 MatchBase와 완전히 동일하지만,
    # 나중에 "생성 시에만 필요한 필드"가 있으면 여기에 추가하면 됨.
    pass


# 🔹 수정용: PUT/PATCH /matches/{id} 에서 사용하는 요청 바디
class MatchUpdate(BaseModel):
    # 전부 Optional로 두는 이유:
    # 일부 필드만 보내서 부분 수정할 수 있게 하기 위함.
    title: Optional[str] = None
    description: Optional[str] = None
    sport: Optional[str] = None
    location: Optional[str] = None

    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    max_people: Optional[int] = None

    # 상태도 수정 가능하도록 열어둠 (예: OPEN → CLOSED)
    status: Optional[str] = None


# 🔹 응답용: 클라이언트에 리턴할 때 사용하는 스키마
class Match(MatchBase):
    id: int                              # 매칭 고유 ID
    owner_id: Optional[int] = None       # 작성자 ID (나중에 유저 시스템 붙이면 필수로)
    status: str                          # OPEN / CLOSED / CANCELLED
    current_people: int                  # 현재 참여 인원

    created_at: datetime                 # 생성 시각
    updated_at: datetime                 # 마지막 수정 시각

    # SQLAlchemy 모델에서 바로 응답 모델로 변환할 수 있게 하는 설정
    # (Pydantic v1의 orm_mode=True 와 같은 역할)
    model_config = ConfigDict(from_attributes=True)

    # 만약 네가 pydantic v1을 쓰고 있다면, 대신 아래 스타일을 써야 함:
    # class Config:
    #     orm_mode = True
