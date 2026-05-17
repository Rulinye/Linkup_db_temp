"""
repositories/workout_session_repo.py
DAO for the Workout_Session table.

UI.md mapping:
    ExerciseExecution:
        start_session()       → start()
    SessionComplete:
        end_session()         → end()

Status: SKELETON.
"""

from typing import Optional, List

from models import WorkoutSession
from constants import Scene
from .db import get_connection


class WorkoutSessionRepo:
    """SQL access for the Workout_Session table."""

    def __init__(self, db_path=None):
        self._db_path = db_path

    # --------------------------------------------------------------
    # Writes
    # --------------------------------------------------------------
    def start(self, date: str, scene: Optional[Scene], started_at: str) -> int:
        """Create a new session row and return its `session_id`.

        Pre-condition: a Daily_Log row for `date` must already exist
                       (enforced by TRG-3 in triggers_and_indexes.sql).
        """
        raise NotImplementedError

    def end(self,
            session_id: int,
            ended_at: str,
            overall_feedback: Optional[int] = None,
            is_completed: bool = True) -> None:
        """Mark a session ended.

        Setting `ended_at` triggers TRG-2 which fills `total_duration_sec`.
        """
        raise NotImplementedError

    # --------------------------------------------------------------
    # Reads
    # --------------------------------------------------------------
    def get(self, session_id: int) -> Optional[WorkoutSession]:
        """Return one session by id, or None."""
        raise NotImplementedError

    def list_by_date(self, date: str) -> List[WorkoutSession]:
        """Return all sessions for a given date."""
        raise NotImplementedError
