# backend/app/db/base.py

from .session import engine
from .base_class import Base

# ⚠️ 여기서 모델을 import 해서 메타데이터에 등록
from ..models.match import Match  # noqa
from ..models.participation import Participation  # noqa


def init_db():
    """
    애플리케이션 시작 시 한 번 호출해서
    모든 테이블을 생성하는 함수.
    """
    Base.metadata.create_all(bind=engine)
