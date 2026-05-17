"""
repositories/daily_log_repo.py
DAO for the Daily_Log table.

UI.md mapping:
    DailyLog screen:
        get_today_log()       → get_today()
        upsert_today_log()    → upsert()

Status: SKELETON.
"""

from typing import Optional

from models import DailyLog
from .db import get_connection


class DailyLogRepo:
    """SQL access for the Daily_Log table (one row per calendar day)."""

    def __init__(self, db_path=None):
        self._db_path = db_path

    # --------------------------------------------------------------
    # Reads
    # --------------------------------------------------------------
    def get(self, date: str) -> Optional[DailyLog]:
        """Return the log for the given 'YYYY-MM-DD' date, or None."""
        raise NotImplementedError

    def get_today(self) -> Optional[DailyLog]:
        """Convenience: get the log for today (local time)."""
        raise NotImplementedError

    # --------------------------------------------------------------
    # Writes
    # --------------------------------------------------------------
    def upsert(self, log: DailyLog) -> None:
        """Insert-or-update Daily_Log row keyed by `date`.

        Serialization rules:
            log.fatigue_by_part → JSON TEXT
                e.g. {BodyPart.NECK: 7} → '{"neck": 7}'
            log.manual_scene    → enum.value or NULL

        v2 NOTE: `mental_condition_score` is the single subjective rating
                 (0~10, 10 = best) covering sleep + mood + stress.
                 The old separate sleep_hours / mood_score / fatigue_score
                 columns are removed.
        """
        raise NotImplementedError
