"""
repositories/stats_repo.py
DAO for aggregate statistics across Workout_Session / Workout_History / Daily_Log.

UI.md mapping:
    Dashboard:
        get_recent_stats()    → recent_stats()
        오늘 누적 / 시간대별 표시 → daily_total_minutes() + list_today_chunks()
    History:
        get_recent_stats()    → recent_stats()
        get_session_list()    → daily_history()

Status: SKELETON.
"""

from dataclasses import dataclass
from typing import List

from models import WorkoutSession
from .db import get_connection
from .user_profile_repo import UserProfileRepo


@dataclass
class RecentStats:
    """Aggregate statistics for the Dashboard / History screens.

    Fields:
        completion_rate : 목표 달성한 날 / 전체 날 (0.0~1.0)
        streak_days     : 연속으로 목표 달성한 일수
        total_chunks    : 기간 내 총 chunk 수
        total_minutes   : 기간 내 총 운동 분
    """
    completion_rate: float
    streak_days: int
    total_chunks: int
    total_minutes: int


@dataclass
class DailyHistorySummary:
    """Per-day aggregated summary for History screen (1 row = 하루치)."""
    date: str                   # 'YYYY-MM-DD'
    total_minutes: int          # 그 날 누적 운동 분
    chunk_count: int            # 그 날 chunk 수
    goal_met: bool              # daily_total_goal_min 달성 여부


class StatsRepo:
    """SQL access for aggregate queries (read-only).

    Holds a UserProfileRepo because daily_goal_met / recent_stats / daily_history
    all need to compare against UserProfile.daily_total_goal_min.
    """

    def __init__(self, db_path=None):
        self._db_path = db_path
        self._user_repo = UserProfileRepo(db_path)

    # --------------------------------------------------------------
    # Aggregated stats (Dashboard + History)
    # --------------------------------------------------------------
    def recent_stats(self, days: int = 7) -> RecentStats:
        """Compute stats over the last `days` calendar days (inclusive of today).

        「완료」 = 그 날 누적 운동 분 ≥ daily_total_goal_min.
        Used by Dashboard (default 7) and History (configurable window).
        """
        raise NotImplementedError

    def daily_history(self, limit: int = 50) -> List[DailyHistorySummary]:
        """Return most recent days with at least one workout, newest first.

        Used by the History screen list view (일별 집계).
        """
        raise NotImplementedError

    # --------------------------------------------------------------
    # Today-specific (Dashboard)
    # --------------------------------------------------------------
    def daily_total_minutes(self, date: str) -> int:
        """특정 날짜의 누적 운동 분 (Dashboard '오늘 누적' 표시용).

        SUM(Workout_Session.total_duration_sec) / 60 WHERE date = ?
        """
        raise NotImplementedError

    def daily_goal_met(self, date: str) -> bool:
        """특정 날짜 목표 달성 여부.

        daily_total_minutes(date) >= UserProfile.daily_total_goal_min.
        """
        raise NotImplementedError

    def list_today_chunks(self, date: str) -> List[WorkoutSession]:
        """오늘 모든 chunk 시간순 (Dashboard 의 「10:00 시작 5분」 표시용)."""
        raise NotImplementedError
