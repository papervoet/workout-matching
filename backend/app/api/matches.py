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
# X-User-Id header or default user fallback
# -------------------------------
def get_current_user_id(x_user_id: Optional[int] = Header(default=None)) -> int:
    """
    Temporary auth shim.
    - If X-User-Id header is provided, use it
    - Otherwise fall back to user 1
    """
    if x_user_id is not None:
        return x_user_id
    return 1


# -------------------------------
# 1. Create match - POST /matches/
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
        owner_id=current_user_id,  # creator
        status="OPEN",             # default status
        current_people=0,          # initial people
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


# -------------------------------
# 2. List matches - GET /matches/
# -------------------------------
@router.get("/", response_model=List[Match])
def list_matches(
    db: Session = Depends(get_db),
    date_param: Optional[date] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    sport: Optional[str] = None,
    only_open: bool = True,
    sido: Optional[str] = None,    # city/province
    gungu: Optional[str] = None,   # district/county
    dong: Optional[str] = None,    # neighborhood
):
    """
    List matches with optional filters

    - ?date_param=2025-11-30 : specific date
    - ?from_date=...&to_date=... : date range filter
    - ?sport=football : sport filter
    - ?only_open=true : only OPEN status
    - ?sido=...&gungu=...&dong=... : location prefix filter (partial string)
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

    # Location prefix filter (sido/gungu/dong)
    if sido or gungu or dong:
        parts: List[str] = []
        if sido:
            parts.append(sido.strip())
        if gungu:
            parts.append(gungu.strip())
        if dong:
            parts.append(dong.strip())

        prefix = " ".join(parts)
        like_pattern = f"{prefix}%"
        query = query.filter(MatchModel.location.ilike(like_pattern))

    query = query.order_by(MatchModel.date, MatchModel.start_time, MatchModel.id)
    return query.all()


# -------------------------------
# 3. Get a match - GET /matches/{match_id}
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
# 4. Update match - PUT /matches/{match_id}
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
# 5. Delete match - DELETE /matches/{match_id}
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
# 6. Cancel match - POST /matches/{match_id}/cancel
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
# 7. Join match - POST /matches/{match_id}/join
# -------------------------------
@router.post("/{match_id}/join", response_model=Match)
def join_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    # Ensure match exists
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Status check
    if match.status != "OPEN":
        raise HTTPException(status_code=400, detail="Match is not open for joining.")

    # Capacity check
    if match.current_people >= match.max_people:
        raise HTTPException(status_code=400, detail="Match is full.")

    # Already joined?
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

    participation = ParticipationModel(
        match_id=match_id,
        user_id=current_user_id,
        status="JOINED",
    )
    db.add(participation)

    match.current_people += 1

    db.commit()
    db.refresh(match)
    return match


# -------------------------------
# 8. Leave match - POST /matches/{match_id}/leave
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

    participation.status = "CANCELLED"

    if match.current_people > 0:
        match.current_people -= 1

    db.commit()
    db.refresh(match)
    return match


# -------------------------------
# 9. Monthly matches - GET /matches/month/{year}/{month}
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


# -------------------------------
# 10. My created matches - GET /matches/my/created
# -------------------------------
@router.get("/my/created", response_model=List[Match])
def list_my_created_matches(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    only_open: bool = True,
):
    """
    Matches I created
    - only_open=True: only OPEN status
    """

    query = db.query(MatchModel).filter(
        MatchModel.owner_id == current_user_id
    )

    if only_open:
        query = query.filter(MatchModel.status == "OPEN")

    query = query.order_by(MatchModel.date, MatchModel.start_time, MatchModel.id)
    return query.all()


# -------------------------------
# 11. My joined matches - GET /matches/my/joined
# -------------------------------
@router.get("/my/joined", response_model=List[Match])
def list_my_joined_matches(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    only_open: bool = True,
):
    """
    Matches I joined (Participation.status == 'JOINED')
    - only_open=True: only OPEN matches
    """

    query = (
        db.query(MatchModel)
        .join(
            ParticipationModel,
            ParticipationModel.match_id == MatchModel.id,
        )
        .filter(
            ParticipationModel.user_id == current_user_id,
            ParticipationModel.status == "JOINED",
        )
    )

    if only_open:
        query = query.filter(MatchModel.status == "OPEN")

    query = query.order_by(MatchModel.date, MatchModel.start_time, MatchModel.id)
    return query.all()
