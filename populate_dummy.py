# populate_dummy.py

from datetime import date, time, datetime, timedelta
import random

from backend.app.db.session import SessionLocal
from backend.app.models.match import Match

db = SessionLocal()

# -----------------------------
# 농구 장소 리스트
# -----------------------------
locations = [
    "강남구민체육센터",
    "송파구민체육센터",
    "서초종합체육관",
    "마포구민체육센터",
    "성동구민체육센터",
    "광진구민체육센터",
    "잠실 학생체육관",
    "상암 월드컵경기장 농구장",
    "고척스카이돔 농구장",
    "뚝섬 한강 농구코트",
    "이촌 한강 농구코트",
]

# -----------------------------
# 날짜/시간 랜덤 생성
# -----------------------------
def random_date(start_days=1, end_days=20):
    """오늘 기준 N일 뒤 랜덤 날짜 생성"""
    today = date.today()
    delta = random.randint(start_days, end_days)
    return today + timedelta(days=delta)

def random_time():
    """18:00 ~ 22:00 사이 시작 시간 + 2시간 종료 시간"""
    start_hour = random.randint(18, 21)  # 18~21시 중 랜덤
    end_hour = start_hour + 2
    return time(start_hour, 0), time(end_hour, 0)


# -----------------------------
# 더미 데이터 생성 10개
# -----------------------------
dummy_matches = []

for i in range(10):
    start_t, end_t = random_time()

    dummy_matches.append(
        Match(
            title=f"농구 매칭 #{i+1}",
            description="테스트용 더미 농구 매칭",
            sport="농구",
            location=random.choice(locations),
            date=random_date(),
            start_time=start_t,
            end_time=end_t,
            max_people=10,
            owner_id=1,
            status="OPEN",
            current_people=0,
        )
    )

# -----------------------------
# DB 저장
# -----------------------------
for m in dummy_matches:
    db.add(m)

db.commit()
db.close()

print("🔥 더미 농구 매칭 10개 자동 생성 완료!")
