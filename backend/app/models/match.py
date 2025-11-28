# backend/app/models/match.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    DateTime,
)
from sqlalchemy.sql import func
from ..db.base_class import Base



class Match(Base):
    __tablename__ = "matches"

    # 🔹 기본 키
    id = Column(Integer, primary_key=True, index=True)

    # 🔹 매칭 기본 정보 (여기는 너 현재 모델에 맞게 조정해도 됨)
    title = Column(String, nullable=False)          # 매칭 제목
    description = Column(String, nullable=True)     # 설명
    sport = Column(String, nullable=True)           # 종목명 (예: 농구, 풋살) - 선택
    location = Column(String, nullable=False)       # 장소

    date = Column(Date, nullable=False)             # 날짜 (예: 2025-11-30)
    start_time = Column(Time, nullable=False)       # 시작 시간
    end_time = Column(Time, nullable=True)          # 끝나는 시간(선택)

    max_people = Column(Integer, nullable=False)    # 최대 인원

    # ✅ [이번 Step A에서 새로 추가하는 핵심 필드들]
    # ---------------------------------------------

    # 1) 누가 만든 매칭인지 (작성자)
    #    지금은 아직 유저 시스템이 없으니까 nullable=True로 두고,
    #    나중에 Firebase 인증 붙일 때 NOT NULL + 실제 user_id로 교체할 거야.
    owner_id = Column(Integer, nullable=True)

    # 2) 매칭 상태
    #    OPEN   : 모집 중
    #    CLOSED : 자동/수동 마감
    #    CANCELLED : 작성자가 취소
    status = Column(String, nullable=False, default="OPEN")

    # 3) 현재 참여 인원
    #    Participation 테이블 붙이기 전까지는 0으로 두고,
    #    나중에 join/leave 로직에서 증가/감소시키면 됨.
    current_people = Column(Integer, nullable=False, default=0)

    # 🔹 생성/수정 시간 (추적용, 선택이지만 있으면 나중에 엄청 편함)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
