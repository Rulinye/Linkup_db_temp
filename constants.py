"""
constants.py
Team LinkUp — Shared Enum Definitions

All team members MUST reference this single file.
- Frontend: dropdown menus render options from these enums.
- Backend : Pydantic validators check against these values.
- Database: TEXT columns store these exact string values.

Usage:
    from constants import BodyPart, ExerciseCategory, Scene, JobType

    # Validate user input
    assert "neck" in BodyPart.values()

    # Iterate for UI dropdowns
    for part in BodyPart:
        print(part.value, part.label_ko)
"""

from enum import Enum
from typing import List


# ------------------------------------------------------------------
# Base class with common helpers
# ------------------------------------------------------------------
class LabeledEnum(str, Enum):
    """Enum with a Korean label for UI rendering."""

    def __new__(cls, value: str, label_ko: str = ""):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label_ko = label_ko
        return obj

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]

    @classmethod
    def choices_ko(cls) -> List[tuple]:
        """Returns [(value, korean_label), ...] for UI dropdowns."""
        return [(member.value, member.label_ko) for member in cls]


# ------------------------------------------------------------------
# Body parts  (pain_points & contraindications)
# ------------------------------------------------------------------
class BodyPart(LabeledEnum):
    NECK       = ("neck",       "목")
    SHOULDER   = ("shoulder",   "어깨")
    UPPER_BACK = ("upper_back", "등 상부")
    LOWER_BACK = ("lower_back", "허리")
    WRIST      = ("wrist",      "손목")
    KNEE       = ("knee",       "무릎")
    ANKLE      = ("ankle",      "발목")
    HIP        = ("hip",        "고관절")
    ELBOW      = ("elbow",      "팔꿈치")
    EYE        = ("eye",        "눈")


# ------------------------------------------------------------------
# Exercise categories
# ------------------------------------------------------------------
class ExerciseCategory(LabeledEnum):
    STRETCH    = ("stretch",    "스트레칭")
    STRENGTH   = ("strength",   "근력 강화")
    CARDIO     = ("cardio",     "유산소")
    RELAXATION = ("relaxation", "이완/명상")
    MOBILITY   = ("mobility",   "관절 가동성")


# ------------------------------------------------------------------
# Scenes
# ------------------------------------------------------------------
class Scene(LabeledEnum):
    OFFICE = ("office", "사무실")
    HOME   = ("home",   "집")


# ------------------------------------------------------------------
# Job types
# ------------------------------------------------------------------
class JobType(LabeledEnum):
    IT            = ("it",            "IT/개발")
    OFFICE_WORKER = ("office_worker", "사무직")
    STUDENT       = ("student",       "학생")
    MANUAL_LABOR  = ("manual_labor",  "현장직/노동직")
    OTHER         = ("other",         "기타")


# ------------------------------------------------------------------
# Difficulty levels (not an Enum, but a shared constant)
# ------------------------------------------------------------------
DIFFICULTY_MIN = 1
DIFFICULTY_MAX = 3
DIFFICULTY_LABELS_KO = {1: "낮음", 2: "보통", 3: "높음"}

FITNESS_LEVEL_MIN = 1
FITNESS_LEVEL_MAX = 5

FATIGUE_SCORE_MIN = 1
FATIGUE_SCORE_MAX = 10


# ------------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------------
def validate_pain_points(csv_string: str) -> bool:
    """Validate that every item in a comma-separated pain_points
    string is a valid BodyPart value."""
    if not csv_string or csv_string.strip() == "":
        return True
    parts = [p.strip() for p in csv_string.split(",") if p.strip()]
    valid = set(BodyPart.values())
    return all(p in valid for p in parts)


def parse_csv(csv_string: str) -> List[str]:
    """Split a comma-separated TEXT field into a list."""
    if not csv_string or csv_string.strip() == "":
        return []
    return [item.strip() for item in csv_string.split(",") if item.strip()]
