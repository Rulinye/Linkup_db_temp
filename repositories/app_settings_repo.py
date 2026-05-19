"""
repositories/app_settings_repo.py
DAO for the App_Settings table (key-value store).

Wraps low-level key/value access with semantic helper methods for
the most-used keys (onboarding_completed, db_version).

Status: SKELETON.
"""

from typing import Optional

from .db import get_connection


class AppSettingsRepo:
    """SQL access for the App_Settings key-value table."""

    def __init__(self, db_path=None):
        self._db_path = db_path

    # --------------------------------------------------------------
    # Generic key/value access
    # --------------------------------------------------------------
    def get(self, key: str) -> Optional[str]:
        """Return the value for a given setting key, or None."""
        raise NotImplementedError

    def set(self, key: str, value: str) -> None:
        """UPSERT a setting key/value."""
        raise NotImplementedError

    # --------------------------------------------------------------
    # Semantic helpers (commonly used keys)
    # --------------------------------------------------------------
    def is_onboarding_completed(self) -> bool:
        """Return whether onboarding has been completed."""
        raise NotImplementedError

    def mark_onboarding_completed(self) -> None:
        """Set onboarding_completed = 'true'."""
        raise NotImplementedError

    def db_version(self) -> str:
        """Return current DB schema version (e.g. '1', '2')."""
        raise NotImplementedError
