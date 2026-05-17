"""
repositories/exercise_library_repo.py
DAO for the Exercise_Library table (static seed + optionally external library).

UI.md mapping:
    ExerciseExecution:
        get_modified_exercise() → get_modified()

Also used by services/routine_service.py for filter queries.

Status: SKELETON.
"""

from typing import Optional, List

from models import ExerciseLibraryItem
from constants import ExerciseCategory, Scene, BodyPart
from .db import get_connection


class ExerciseLibraryRepo:
    """SQL access for the Exercise_Library table."""

    def __init__(self, db_path=None):
        self._db_path = db_path

    # --------------------------------------------------------------
    # Reads
    # --------------------------------------------------------------
    def get(self, ex_id: str) -> Optional[ExerciseLibraryItem]:
        """Return one exercise by id, or None."""
        raise NotImplementedError

    def get_modified(self, ex_id: str) -> Optional[ExerciseLibraryItem]:
        """Return the easier-version exercise referenced by `modified_ex_id`.

        Used at INPUT.md 5 when user hits "너무 어려워요" (too hard) button.
        """
        raise NotImplementedError

    def list_all(self) -> List[ExerciseLibraryItem]:
        """Return all exercises. Used for routine generation."""
        raise NotImplementedError

    def query(self,
              category: Optional[ExerciseCategory] = None,
              scene: Optional[Scene] = None,
              max_difficulty: Optional[int] = None,
              avoid_body_parts: Optional[List[BodyPart]] = None) -> List[ExerciseLibraryItem]:
        """Filter exercises by routine algorithm constraints.

        Filter semantics:
            category         : exact match
            scene            : LIKE %scene% on suitable_scenes (CSV)
            max_difficulty   : difficulty_level <= max_difficulty
            avoid_body_parts : exclude exercises whose contraindications
                               overlap with avoid_body_parts
        """
        raise NotImplementedError
