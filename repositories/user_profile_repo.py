"""
repositories/user_profile_repo.py
DAO for the User_Profile table.

UI.md mapping:
    Onboarding / ProfileEdit:
        has_user_profile()    → has_profile()
        get_user_profile()    → get()
        save_user_profile()   → save()

Status: SKELETON (signature + docstring only).
"""

from typing import Optional

from models import UserProfile
from .db import get_connection


class UserProfileRepo:
    """SQL access for the single-row User_Profile table (id = 1)."""

    def __init__(self, db_path=None):
        self._db_path = db_path

    # --------------------------------------------------------------
    # Reads
    # --------------------------------------------------------------
    def has_profile(self) -> bool:
        """Return True iff a user profile has been completed.

        Definition of "completed" (TBD):
            Option A: row id=1 exists AND nickname IS NOT NULL.
            Option B: rely on App_Settings.onboarding_completed flag.
        """
        raise NotImplementedError

    def get(self) -> Optional[UserProfile]:
        """Return the single profile row, or None if it does not exist yet."""
        raise NotImplementedError

    # --------------------------------------------------------------
    # Writes
    # --------------------------------------------------------------
    def save(self, profile: UserProfile) -> None:
        """UPSERT the profile row (always id = 1).

        Serialization rules:
            profile.goals                → CSV (Goal.values)
            profile.pain_points          → CSV (BodyPart.values)
            profile.job_type             → enum.value
            profile.notification_enabled → 0/1 INTEGER

        Updates User_Profile.updated_at (handled by TRG-1).
        """
        raise NotImplementedError
