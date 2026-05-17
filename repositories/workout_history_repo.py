"""
repositories/workout_history_repo.py
DAO for the Workout_History table (per-exercise records inside a session).

UI.md mapping:
    ExerciseExecution:
        record_history()      → create()

Status: SKELETON.
"""

from typing import Optional, List

from models import WorkoutHistory
from constants import SessionStatus, BodyPart
from .db import get_connection


class WorkoutHistoryRepo:
    """SQL access for the Workout_History table."""

    def __init__(self, db_path=None):
        self._db_path = db_path

    # --------------------------------------------------------------
    # Writes
    # --------------------------------------------------------------
    def create(self, history: WorkoutHistory) -> int:
        """Insert a Workout_History row, return new `history_id`.

        Serialization rules:
            history.pain_during → CSV (BodyPart.values)
            history.status      → enum.value
            history.is_completed → auto-synced with (status == COMPLETED)

        Called when:
            - Routine is generated (status = PENDING for each item)
            - Exercise finishes / is skipped / aborted (status update via update_status)
        """
        raise NotImplementedError

    def update_status(self,
                       history_id: int,
                       status: SessionStatus,
                       feedback: Optional[int] = None,
                       pain_during: Optional[List[BodyPart]] = None,
                       actual_sets: Optional[int] = None,
                       actual_duration_sec: Optional[int] = None,
                       used_modified: Optional[bool] = None) -> None:
        """Update an existing history row.

        Used at INPUT.md 5 transitions:
            - "현재 진행 중인 동작 제외" → status = SKIPPED
            - "그만두기"                  → status = ABORTED
            - exercise finished           → status = COMPLETED + feedback + pain_during
        """
        raise NotImplementedError

    # --------------------------------------------------------------
    # Reads
    # --------------------------------------------------------------
    def list_by_session(self, session_id: int) -> List[WorkoutHistory]:
        """Return all per-exercise records for a session, ordered by seq_order."""
        raise NotImplementedError
