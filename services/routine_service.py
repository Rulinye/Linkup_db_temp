"""
services/routine_service.py
Business logic for generating workout routines.

UI.md mapping:
    RoutinePreview:
        generate_routine() → generate()

This service does NOT touch SQL directly. It composes the relevant
repositories and runs the routine algorithm in Python.

Status: SKELETON.
"""

from typing import List

from models import ExerciseLibraryItem
from repositories import (
    UserProfileRepo,
    DailyLogRepo,
    ExerciseLibraryRepo,
    StatsRepo,
)


class RoutineService:
    """Generates a personalized routine based on today's remaining minutes.

    Algorithm draft (heuristic은 함수 정리 후 확정):
        1. Compute remaining = daily_total_goal_min - daily_total_minutes(date).
           (clamp at 0; if already met, return empty list)
        2. Fetch UserProfile (daily_total_goal_min, goals, pain_points,
                              pushup/plank/squat).
        3. Fetch today's DailyLog (mental_condition_score, fatigue_by_part,
                                   outdoor_hours).
        4. Compute effective difficulty:
             - Map raw counts (pushup/plank/squat) → 1~3 difficulty.
             - Adjust by mental_condition_score (low → easier).
        5. Build filter set:
             - category mix per Goal (예: muscle_gain → strength heavy).
             - scene = today's chosen scene or User_Profile default.
             - max_difficulty = effective difficulty.
             - avoid_body_parts = pain_points ∪ high-fatigue parts
                                  (예: fatigue_by_part[part] >= 7).
        6. Query Exercise_Library with the filter set.
        7. Compose ordered list whose total duration fits remaining minutes.
           (heuristic TBD: 평균 분/동작 등)
    """

    def __init__(self, db_path=None):
        self._user_repo = UserProfileRepo(db_path)
        self._log_repo = DailyLogRepo(db_path)
        self._lib_repo = ExerciseLibraryRepo(db_path)
        self._stats_repo = StatsRepo(db_path)

    def generate(self, date: str) -> List[ExerciseLibraryItem]:
        """오늘 남은 운동 분에 맞춰 routine 을 생성해 반환.

        사용자에게 「몇 분 있어요?」 를 묻지 않음. 내부에서
        daily_remaining = goal - 누적분 으로 계산.

        Args:
            date: 'YYYY-MM-DD'

        Returns:
            ExerciseLibraryItem 순서있는 list. 총 길이 ≈ daily_remaining.
            daily_remaining ≤ 0 이면 empty list (이미 목표 달성).

        Caller (RoutinePreview 화면) 가 user 에게 보여주고, 확정 시
        ExerciseExecution 흐름이 Workout_Session 생성 + 각 동작별
        Workout_History (status=PENDING) 를 생성한다.
        사용자는 도중에 중단 가능하며, 그만큼만 누적 기록된다.
        """
        raise NotImplementedError

    def get_daily_remaining(self, date: str) -> int:
        """오늘 목표까지 남은 분 (Dashboard 표시용).

        = UserProfile.daily_total_goal_min - StatsRepo.daily_total_minutes(date).
        음수는 0 으로 clamp.
        """
        raise NotImplementedError
