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
)


class RoutineService:
    """Generates a personalized routine matching the user-provided session duration.

    Algorithm draft (heuristic은 함수 정리 후 확정):
        1. Fetch UserProfile (goals, pain_points, pushup/plank/squat).
        2. Fetch today's DailyLog (mental_condition_score, fatigue_by_part,
                                   outdoor_hours).
        3. Compute effective difficulty:
             - Map raw counts (pushup/plank/squat) → 1~3 difficulty.
             - Adjust by mental_condition_score (low → easier).
        4. Build filter set:
             - category mix per Goal (예: muscle_gain → strength heavy).
             - scene = today's chosen scene or User_Profile default.
             - max_difficulty = effective difficulty.
             - avoid_body_parts = pain_points ∪ high-fatigue parts
                                  (예: fatigue_by_part[part] >= 7).
        5. Query Exercise_Library with the filter set.
        6. Compose ordered list whose total duration fits available_min.
           (heuristic TBD: 평균 분/동작 등)
    """

    def __init__(self, db_path=None):
        self._user_repo = UserProfileRepo(db_path)
        self._log_repo = DailyLogRepo(db_path)
        self._lib_repo = ExerciseLibraryRepo(db_path)

    def generate(self, date: str, available_min: int) -> List[ExerciseLibraryItem]:
        """사용자가 「지금 X 분 운동할 거예요」 라고 입력한 시간에 맞춰 routine 생성.

        Args:
            date: 'YYYY-MM-DD' — 오늘 (DailyLog 조회용)
            available_min: 사용자가 입력한 이번 chunk 분 수

        Returns:
            ExerciseLibraryItem 순서있는 list. 총 길이 ≈ available_min.

        Caller (RoutinePreview 화면) 가 user 에게 보여주고, 확정 시
        ExerciseExecution 흐름이 Workout_Session 생성 + 각 동작별
        Workout_History (status=PENDING) 를 생성한다.
        사용자는 도중에 중단 가능하며, 그만큼만 누적 기록된다.
        하루 총 운동 분은 chunk 들의 단순 합산.
        """
        raise NotImplementedError
