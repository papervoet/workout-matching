# backend/app/api/sports.py

from fastapi import APIRouter, HTTPException

router = APIRouter()

SPORTS = [
    {
        "code": "basketball",
        "name": "농구",
        "status": "active",
        "categories": [
            {"code": "pickup", "name": "픽업게임"},
            {"code": "scrimmage", "name": "연습게임"},
            {"code": "guest", "name": "게스트 구인"},
        ],
    },
    {
        "code": "tennis",
        "name": "테니스",
        "status": "coming_soon",
        "categories": [],
    },
    {
        "code": "soccer",
        "name": "축구",
        "status": "coming_soon",
        "categories": [],
    },
]


@router.get("/")
def list_sports():
    return SPORTS


@router.get("/{sport_code}")
def get_sport(sport_code: str):
    for s in SPORTS:
        if s["code"] == sport_code:
            return s
    raise HTTPException(status_code=404, detail="Sport not found")
