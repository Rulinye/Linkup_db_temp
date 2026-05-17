"""
repositories/  (DAO layer)

Each module owns SQL access for a single table. Business code imports
the Repo class and works with dataclass objects defined in models.py.

Status: all repos are SKELETONs (NotImplementedError).
        SQL implementations are filled in after team review of
        docs/FUNCTION_LIST.md.
"""

from .db import get_connection, init_db
from .user_profile_repo import UserProfileRepo
from .daily_log_repo import DailyLogRepo
from .workout_session_repo import WorkoutSessionRepo
from .workout_history_repo import WorkoutHistoryRepo
from .exercise_library_repo import ExerciseLibraryRepo
from .stats_repo import StatsRepo, RecentStats, DailyHistorySummary
from .app_settings_repo import AppSettingsRepo

__all__ = [
    "get_connection",
    "init_db",
    "UserProfileRepo",
    "DailyLogRepo",
    "WorkoutSessionRepo",
    "WorkoutHistoryRepo",
    "ExerciseLibraryRepo",
    "StatsRepo",
    "RecentStats",
    "DailyHistorySummary",
    "AppSettingsRepo",
]
