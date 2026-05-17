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


@dataclass
class RecentStats:
    """Aggregate statistics for the Dashboard / History screens.

    Fields:
        active_days     : 기간 내 운동 한 적 있는 날 수
        streak_days     : 연속 운동 일수 (오늘 기준)
        total_chunks    : 기간 내 총 chunk 수
        total_minutes   : 기간 내 총 운동 분
    """
    active_days: int
    streak_days: int
    total_chunks: int
    total_minutes: int


@dataclass
class DailyHistorySummary:
    """Per-day aggregated summary for History screen (1 row = 하루치)."""
    date: str                   # 'YYYY-MM-DD'
    total_minutes: int          # 그 날 누적 운동 분
    chunk_count: int            # 그 날 chunk 수


class StatsRepo:
    """SQL access for aggregate queries (read-only)."""

    def __init__(self, db_path=None):
        self._db_path = db_path

    # --------------------------------------------------------------
    # Aggregated stats (Dashboard + History)
    # --------------------------------------------------------------
    def recent_stats(self, days: int = 7) -> RecentStats:
        """Compute stats over the last `days` calendar days (inclusive of today).

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

    def list_today_chunks(self, date: str) -> List[WorkoutSession]:
        """오늘 모든 chunk 시간순 (Dashboard 의 「10:00 시작 5분」 표시용)."""
        raise NotImplementedError
