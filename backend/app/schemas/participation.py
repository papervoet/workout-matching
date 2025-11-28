# backend/app/schemas/participation.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ParticipationBase(BaseModel):
    match_id: int
    user_id: int


class ParticipationCreate(ParticipationBase):
    # join/leave에서는 직접 안 쓸 가능성이 크지만, 형태만 맞춰둔 것
    pass


class Participation(ParticipationBase):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    # pydantic v1이면:
    # class Config:
    #     orm_mode = True
