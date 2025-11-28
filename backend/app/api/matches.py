# backend/app/api/matches.py

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.match import Match as MatchModel
from ..models.participation import Participation as ParticipationModel
from ..schemas import Match, MatchCreate, MatchUpdate

router = APIRouter(prefix="/matches", tags=["matches"])


# -------------------------------
# 임시 유저(작성자) 의존성
# -------------------------------
def get_current_user_id(x_user_id: Optional[int] = Header(default=1)):
    """
    개발 단계용 임시 로그인.

    - 실제 서비스에서는 Firebase 등에서 user_id를 추출해야 함.
    - 지금은 X-User-Id 헤더가 오면 그 값을 쓰고,
      안 오면 기본값으로 1번 유저로 간주.
    """
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header required in dev mode.",
        )
    return x_user_id


# -------------------------------
# 1. 매칭 생성 - POST /matches/
# -------------------------------
@router.post("/", response_model=Match, status_code=status.HTTP_201_CREATED)
def create_match(
    match_in: MatchCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if hasattr(match_in, "model_dump"):
        data = match_in.model_dump()
    else:
        data = match_in.dict()

    db_match = MatchModel(
        **data,
        owner_id=current_user_id,  # 작성자
        status="OPEN",             # 기본 상태
        current_people=0,          # 초기 인원
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


# -------------------------------
# 2. 매칭 리스트 조회 - GET /matches/
# -------------------------------
@router.get("/", response_model=List[Match])
def list_matches(
    db: Session = Depends(get_db),
    date_param: Optional[date] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    sport: Optional[str] = None,
    only_open: bool = True,
):
    """
    매칭 리스트 조회 + 필터

    - ?date_param=2025-11-30 : 해당 날짜만
    - ?from_date=...&to_date=... : 기간 필터
    - ?sport=농구 : 종목 필터
    - ?only_open=true : OPEN 상태만
    """
    query = db.query(MatchModel)

    if only_open:
        query = query.filter(MatchModel.status == "OPEN")

    if sport:
        query = query.filter(MatchModel.sport == sport)

    if date_param:
        query = query.filter(MatchModel.date == date_param)
    else:
        if from_date:
            query = query.filter(MatchModel.date >= from_date)
        if to_date:
            query = query.filter(MatchModel.date <= to_date)

    query = query.order_by(MatchModel.date, MatchModel.start_time, MatchModel.id)
    return query.all()


# -------------------------------
# 3. 단일 매칭 조회 - GET /matches/{match_id}
# -------------------------------
@router.get("/{match_id}", response_model=Match)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


# -------------------------------
# 4. 매칭 수정 - PUT /matches/{match_id}
# -------------------------------
@router.put("/{match_id}", response_model=Match)
def update_match(
    match_id: int,
    match_in: MatchUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.owner_id is not None and match.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this match.")

    if hasattr(match_in, "model_dump"):
        update_data = match_in.model_dump(exclude_unset=True)
    else:
        update_data = match_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(match, field, value)

    db.commit()
    db.refresh(match)
    return match


# -------------------------------
# 5. 매칭 삭제 - DELETE /matches/{match_id}
# -------------------------------
@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.owner_id is not None and match.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this match.")

    db.delete(match)
    db.commit()
    return


# -------------------------------
# 6. 매칭 취소 - POST /matches/{match_id}/cancel
# -------------------------------
@router.post("/{match_id}/cancel", response_model=Match)
def cancel_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.owner_id is not None and match.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this match.")

    if match.status == "CANCELLED":
        return match

    match.status = "CANCELLED"
    db.commit()
    db.refresh(match)
    return match


# -------------------------------
# 7. 매칭 참여 - POST /matches/{match_id}/join
# -------------------------------
@router.post("/{match_id}/join", response_model=Match)
def join_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    # 매칭 존재 확인
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # 상태 체크
    if match.status != "OPEN":
        raise HTTPException(status_code=400, detail="Match is not open for joining.")

    # 인원 초과 체크
    if match.current_people >= match.max_people:
        raise HTTPException(status_code=400, detail="Match is full.")

    # 이미 참여중인지 체크 (JOINED 상태)
    existing = (
        db.query(ParticipationModel)
        .filter(
            ParticipationModel.match_id == match_id,
            ParticipationModel.user_id == current_user_id,
            ParticipationModel.status == "JOINED",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already joined this match.")

    # Participation 생성
    participation = ParticipationModel(
        match_id=match_id,
        user_id=current_user_id,
        status="JOINED",
    )
    db.add(participation)

    # 현재 인원 +1
    match.current_people += 1

    db.commit()
    db.refresh(match)
    return match


# -------------------------------
# 8. 매칭 참여 취소 - POST /matches/{match_id}/leave
# -------------------------------
@router.post("/{match_id}/leave", response_model=Match)
def leave_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # 지금 JOINED 상태의 Participation 찾기
    participation = (
        db.query(ParticipationModel)
        .filter(
            ParticipationModel.match_id == match_id,
            ParticipationModel.user_id == current_user_id,
            ParticipationModel.status == "JOINED",
        )
        .first()
    )

    if not participation:
        raise HTTPException(status_code=400, detail="You are not joined in this match.")

    # 상태 변경 (soft cancel)
    participation.status = "CANCELLED"

    # 현재 인원 -1 (0 아래로는 안내려가게)
    if match.current_people > 0:
        match.current_people -= 1

    db.commit()
    db.refresh(match)
    return match


# -------------------------------
# 9. 특정 월 매칭 조회 - GET /matches/month/{year}/{month}
# -------------------------------
@router.get("/month/{year}/{month}", response_model=List[Match])
def list_matches_by_month(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    only_open: bool = True,
):
    start_date = date(year=year, month=month, day=1)

    if month == 12:
        end_date = date(year=year + 1, month=1, day=1)
    else:
        end_date = date(year=year, month=month + 1, day=1)

    query = db.query(MatchModel).filter(
        MatchModel.date >= start_date,
        MatchModel.date < end_date,
    )

    if only_open:
        query = query.filter(MatchModel.status == "OPEN")

    query = query.order_by(MatchModel.date, MatchModel.start_time, MatchModel.id)
    return query.all()

