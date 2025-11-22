# backend/app/api/matches.py

from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..schemas.match import Match, MatchCreate, MatchUpdate
from ..db.session import get_db
from ..models.match import MatchModel

router = APIRouter()


# 1) 전체 목록 조회
@router.get("/", response_model=List[Match])
def list_matches(db: Session = Depends(get_db)):
    matches = db.query(MatchModel).all()
    return matches


# 2) 단일 조회
@router.get("/{match_id}", response_model=Match)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


# 3) 생성
@router.post("/", response_model=Match)
def create_match(match_in: MatchCreate, db: Session = Depends(get_db)):
    match = MatchModel(
        sport=match_in.sport,
        game_type=match_in.game_type,
        game_time=match_in.game_time,
        level=match_in.level,
        place=match_in.place,
        note=match_in.note,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


# 4) 수정
@router.put("/{match_id}", response_model=Match)
def update_match(match_id: int, match_in: MatchUpdate, db: Session = Depends(get_db)):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.sport = match_in.sport
    match.game_type = match_in.game_type
    match.game_time = match_in.game_time
    match.level = match_in.level
    match.place = match_in.place
    match.note = match_in.note

    db.commit()
    db.refresh(match)
    return match


# 5) 삭제
@router.delete("/{match_id}")
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    db.delete(match)
    db.commit()
    return {"detail": "Match deleted"}

