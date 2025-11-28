# backend/app/models/participation.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from ..db.base_class import Base


class Participation(Base):
    __tablename__ = "participations"

    id = Column(Integer, primary_key=True, index=True)

    # 어떤 매칭에 대한 참여인지
    match_id = Column(
        Integer,
        ForeignKey("matches.id", ondelete="CASCADE"),  # 매칭 삭제 시 참여도 같이 삭제
        nullable=False,
        index=True,
    )

    # 누가 참여했는지 (지금은 User 테이블이 없으므로 단순 int로)
    user_id = Column(Integer, nullable=False, index=True)

    # 상태: JOINED / CANCELLED 등
    status = Column(String, nullable=False, default="JOINED")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
