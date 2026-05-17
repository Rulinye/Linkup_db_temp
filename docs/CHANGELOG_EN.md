# DB Schema Changelog (English)

This document tracks all changes to the LinkUp DB schema and related code (constants / models / repositories).
Korean version: [CHANGELOG_KOR.md](CHANGELOG_KOR.md)

Authoring rules:
- Every change must include **reason**, **scope of impact**, and **rollback plan**.
- The source of each change (INPUT.md / UI.md / team meeting / external library) must be cited.
- Undecided items are grouped in a dedicated section for the next meeting.

---

## v2.2 — 2026-05-17 (Planned, NOT executed)

### Background

Adopted review feedback. Instead of a "daily goal" model, switched to **"user inputs available time each session; daily total = simple sum of all chunks"**. This better matches the meeting's "3~10 min split & accumulate" intent.

### Schema Changes

| Table | Change |
|---|---|
| `User_Profile` | **DROP** `daily_total_goal_min` (column added in v2.1) |

### Constants Changes

- **Removed**: `DAILY_GOAL_MIN`, `DAILY_GOAL_MAX`, `DAILY_GOAL_DEFAULT`

### DTO (`models.py`) Changes

- `UserProfile.daily_total_goal_min` **removed**

### DAO / Service Changes

| Change | Detail |
|---|---|
| `RoutineService.generate(date)` → `generate(date, available_min)` | Takes user-input minutes each session |
| `RoutineService.get_daily_remaining()` | **Removed** (no daily goal) |
| `StatsRepo.daily_goal_met()` | **Removed** (no daily goal) |
| `StatsRepo.__init__` | `UserProfileRepo` dependency removed (v2.1 fix no longer needed) |
| `RecentStats` | `completion_rate` → `active_days` (count of days with any workout) |
| `DailyHistorySummary` | `goal_met` field removed |

Function count: 31 → **29**.

### Impact

- **Breaking**: `daily_total_goal_min` column dropped (v2.1 was never executed, so no real data lost)
- **Non-breaking**: everything else (still SKELETON stage)

### Rollback

`schema_v2.sql` never executed → no rollback needed.

---

## v2.1 — 2026-05-17 (Planned, NOT executed)

### Background

Reflects 5/17 team meeting decisions:
- All equipment-requiring exercises excluded (bodyweight only).
- Workout split into 3~10 min chunks, daily accumulation 15~20 min.
- Users do **not** input chunk length each time. Onboarding sets a daily goal; routine algorithm uses `daily_remaining` (= goal − accumulated).
- "Safety" wording replaced with "no-strain / minimal exercise" (doc-level).
- Disease classification removed; body-part filtering only (schema unchanged).

### Schema Changes (additional from v2)

| Table | Change |
|---|---|
| `User_Profile` | **DROP** `preferred_duration_min` (v1 column) |
| `User_Profile` | **ADD** `daily_total_goal_min INTEGER DEFAULT 15 CHECK 5~60` |
| `Exercise_Library` | v2's `equipment` ADD COLUMN **canceled** |

### Constants Changes

- **Removed**: `Equipment` enum (10 values)
- **Removed**: `Scene.GYM`
- **Removed**: `validate_equipment_list()`
- **Kept**: `MENTAL_CONDITION_MIN/MAX`, `OUTDOOR_HOURS_MIN/MAX`, etc.
- **Added**: `DAILY_GOAL_MIN = 5`, `DAILY_GOAL_MAX = 60`, `DAILY_GOAL_DEFAULT = 15`

### DTO (`models.py`) Changes

- `UserProfile.available_equipment` **removed**
- `UserProfile.preferred_duration_min` **removed**
- `UserProfile.daily_total_goal_min` **added** (default 15)
- `ExerciseLibraryItem.equipment` **removed**

### DAO Changes

| Change | Detail |
|---|---|
| `ExerciseLibraryRepo.query()` | `equipment_in` parameter removed |
| `StatsRepo.session_list()` | → `daily_history()`, returns `DailyHistorySummary` |
| `StatsRepo.recent_stats()` | "completed" redefined (session-based → daily-accumulated ≥ goal) |
| `StatsRepo` (new) | `daily_total_minutes(date)` |
| `StatsRepo` (new) | `daily_goal_met(date)` |
| `StatsRepo` (new) | `list_today_chunks(date)` |
| `RoutineService.generate(date)` | Signature unchanged. Internally computes `daily_remaining`. |
| `RoutineService` (new) | `get_daily_remaining(date)` |
| **New class** `AppSettingsRepo` | 7 methods (`get`/`set`/`is_onboarding_completed`/`mark_onboarding_completed`/`get_theme`/`get_language`/`db_version`) |

Total functions: **31** (UserProfile 3 + DailyLog 3 + WorkoutSession 4 + WorkoutHistory 3 + ExerciseLibrary 4 + Stats 5 + AppSettings 7 + RoutineService 2).

### New Files

- `docs/FUNCTION_LIST.md` — 31 functions + NFR mapping (for review)
- `repositories/app_settings_repo.py` — `AppSettingsRepo` skeleton

### Impact

- **Breaking**: `preferred_duration_min` dropped → any code referencing it errors out (data accumulated since v1 lost).
- **Non-breaking**: new column / new class / new methods are additive.
- **Docs**: `README.md`, `requirement_analysis.md`, ER diagram need updates (TODO).

### Rollback

If `schema_v2.sql` not yet executed, no rollback needed.
After execution, restore from DB backup.

---

## v2 — 2026-05-16 (Planned, NOT executed)

### 1. Metadata

| Field | Value |
|---|---|
| Status | **Planned** — `schema_v2.sql` not yet executed |
| Confirmation date | After team meeting on 2026-05-17 |
| Previous version | v1 ([schema.sql](../schema.sql)) |
| Apply command | `sqlite3 linkup.db < schema_v2.sql` (after meeting) |

### 2. Background

Three inputs drove this revision in May 2026:

1. **INPUT.md** — New onboarding/daily scenarios (job / goals / period / frequency / equipment / pain / fitness test / notifications / outdoor time / stress)
2. **UI.md** — Per-screen DB Interface list (basis for DAO design)
3. **Team meeting decisions** — Unified mental condition score, no server/login, equipment included (see § 3 below)
4. **External exercise library prep** — Reviewing yuhonas/free-exercise-db and others

### 3. Team Meeting Decisions

- No server/login → Current single-user local SQLite design unchanged.
- Sleep + mood + stress → Merged into a **single score** `mental_condition_score` 0–10 (10 = best).
- Equipment → Add `User_Profile.available_equipment` column.

---

### 4. Detailed Changes

#### 4.1 `User_Profile` Table

**Dropped columns:**

| Column | Reason |
|---|---|
| `fitness_level INTEGER 1~5` | Abstract self-rating → replaced by 3 concrete measurements (`pushup_max`, `plank_max_sec`, `squat_max`) per INPUT.md 2-7. The 1–5 level is now computed on-the-fly inside the routine algorithm from the raw counts. |

**Added columns:**

| Column | Type | Default | CHECK | Source | Description |
|---|---|---|---|---|---|
| `avatar_path` | TEXT | NULL | — | INPUT.md 1-2 | Local path to profile photo (BLOB not used) |
| `goals` | TEXT | `''` | — | INPUT.md 2-2 | Workout goals, CSV of `Goal` enum. e.g. `'muscle_gain,diet'` |
| `goal_duration_weeks` | INTEGER | NULL | 1~24 | INPUT.md 2-3 | Goal period in weeks |
| `weekly_frequency` | INTEGER | NULL | 1~7 | INPUT.md 2-4 | Weekly workout frequency |
| `available_equipment` | TEXT | `''` | — | INPUT.md 2-8 | Owned equipment, CSV of `Equipment` enum. e.g. `'dumbbell,band'` |
| `notification_enabled` | INTEGER | `1` | 0 or 1 | INPUT.md 2-9 | Notification on/off. 0=off, 1=on |
| `pushup_max` | INTEGER | NULL | ≥ 0 | INPUT.md 2-7 | Max push-up reps. NULL = "I don't know" |
| `plank_max_sec` | INTEGER | NULL | ≥ 0 | INPUT.md 2-7 | Max plank hold (seconds). NULL = "I don't know" |
| `squat_max` | INTEGER | NULL | ≥ 0 | INPUT.md 2-7 | Max squat reps. NULL = "I don't know" |

**Unchanged columns:**
`id`, `nickname`, `birth_year`, `height_cm`, `weight_kg`, `job_type`, `pain_points`, `preferred_duration_min`, `daily_step_goal`, `reminder_interval_min`, `created_at`, `updated_at`

#### 4.2 `Daily_Log` Table

**Dropped columns:**

| Column | Reason |
|---|---|
| `sleep_hours REAL` | Team decision: merged into `mental_condition_score` (no separate UI input) |
| `mood_score INTEGER 1~5` | Team decision: merged into `mental_condition_score` |
| `fatigue_score INTEGER 1~10` | INPUT.md 3-2-2: single score → per body part → replaced by `fatigue_by_part` |

**Added columns:**

| Column | Type | Default | CHECK | Source | Description |
|---|---|---|---|---|---|
| `mental_condition_score` | INTEGER | NULL | 0~10 | Team meeting | Unified mental condition score. **10 = best** (covers sleep + mood + stress) |
| `outdoor_hours` | REAL | NULL | 0~16 | INPUT.md 3-2-1 | Outdoor activity time in hours |
| `fatigue_by_part` | TEXT | `'{}'` | — | INPUT.md 3-2-2 | Per-body-part fatigue as JSON. e.g. `{"neck":7,"shoulder":3}` |

**`fatigue_by_part` JSON contract:**
- key: `BodyPart` enum value (`neck`, `shoulder`, `lower_back`, …)
- value: integer 1~10
- Body parts with no pain are **omitted** (sparse format)
- Empty object `{}` = no fatigue anywhere

**Unchanged columns:**
`date`, `step_count`, `manual_scene`, `created_at`

#### 4.3 `Workout_History` Table

**Added column:**

| Column | Type | Default | CHECK | Source | Description |
|---|---|---|---|---|---|
| `status` | TEXT | `'pending'` | enum | INPUT.md 5 | Exercise status. `pending` / `completed` / `skipped` / `aborted` |

**Status meanings:**
| Value | Meaning | INPUT.md 5 mapping |
|---|---|---|
| `pending` | Not yet performed (default) | At session start |
| `completed` | Finished normally | — |
| `skipped` | Skipped via "exclude current" | "현재 진행 중인 동작 제외" |
| `aborted` | Stopped via "quit" | "그만두기" |

**Handling of existing `is_completed BOOLEAN` column:**
- **Not dropped** for backward compatibility
- DAO will auto-sync with `status = 'completed'`
- Removal reviewed at 5/17 meeting

**Unchanged columns:**
`history_id`, `session_id`, `ex_id`, `seq_order`, `actual_sets`, `actual_duration_sec`, `is_completed`, `used_modified`, `feedback`, `pain_during`

#### 4.4 `Exercise_Library` Table

**Added column:**

| Column | Type | Default | Source | Description |
|---|---|---|---|---|
| `equipment` | TEXT | `'none'` | Linked to INPUT.md 2-8 | Required equipment (single value). `Equipment` enum. Matched against `User_Profile.available_equipment` for filtering |

**Pending additions (after external library decision on 5/17):**
- `force` TEXT — push / pull / static
- `mechanic` TEXT — compound / isolation
- `primary_muscle` TEXT — split from current `target_muscle`
- `secondary_muscle` TEXT — split from current `target_muscle`
- `images` TEXT — JSON array, replacing single `media_path`

#### 4.5 `Workout_Session`, `App_Settings` Tables

**No changes.**

---

### 5. constants.py Changes

**New enums:**

#### `Goal` (workout goals, INPUT.md 2-2)
| value | label_ko |
|---|---|
| `muscle_gain` | 근육량 증가 |
| `diet` | 다이어트 |
| `lifestyle` | 생활 습관 개선 |
| `basic_fitness` | 기초 체력 증가 |
| `none` | 없음 |

#### `Equipment` (owned equipment, INPUT.md 2-8)
| value | label_ko |
|---|---|
| `dumbbell` | 덤벨 |
| `band` | 밴드 |
| `pushup_bar` | 푸쉬업 바 |
| `pull_up_bar` | 철봉 |
| `kettlebell` | 케틀벨 |
| `stepper` | 스텝퍼 |
| `indoor_bike` | 실내 자전거 |
| `gym_ball` | 짐볼 |
| `foam_roller` | 폼롤러 |
| `none` | 없음 |

#### `SessionStatus` (exercise status, INPUT.md 5)
| value | label_ko |
|---|---|
| `pending` | 대기 |
| `completed` | 완료 |
| `skipped` | 건너뜀 |
| `aborted` | 중단됨 |

**Modified enums:**

| Enum | Change |
|---|---|
| `Scene` | Added `gym` (`헬스장`). `office`, `home` kept. ⚠️ Removal of `office` to be decided on 5/17 |

**Added constants:**
```python
MENTAL_CONDITION_MIN = 0
MENTAL_CONDITION_MAX = 10
OUTDOOR_HOURS_MIN = 0
OUTDOOR_HOURS_MAX = 16
GOAL_DURATION_MIN = 1
GOAL_DURATION_MAX = 24
WEEKLY_FREQUENCY_MIN = 1
WEEKLY_FREQUENCY_MAX = 7
PREFERRED_DURATION_MIN = 10
PREFERRED_DURATION_MAX = 30
```

**Removed constants:**
```python
FITNESS_LEVEL_MIN  # fitness_level column dropped
FITNESS_LEVEL_MAX  # ditto
```

---

### 6. New Files

| File | Role | Notes |
|---|---|---|
| `models.py` | Dataclass for 6 tables | Data containers between business logic and DAO |
| `schema_v2.sql` | v1 → v2 migration script | **Execute after meeting** |
| `repositories/__init__.py` | Package init | — |
| `repositories/db.py` | SQLite connection helper | `get_connection()`, etc. |
| `repositories/user_profile_repo.py` | UserProfileRepo (DAO) skeleton | Matches UI.md `has_user_profile`, `get_user_profile`, `save_user_profile` |
| `repositories/daily_log_repo.py` | DailyLogRepo (DAO) skeleton | Matches `get_today_log`, `upsert_today_log` |
| `repositories/workout_session_repo.py` | WorkoutSessionRepo (DAO) skeleton | Matches `start_session`, `end_session` |
| `repositories/workout_history_repo.py` | WorkoutHistoryRepo (DAO) skeleton | Matches `record_history` |
| `repositories/exercise_library_repo.py` | ExerciseLibraryRepo (DAO) skeleton | Matches `get_modified_exercise` |
| `repositories/stats_repo.py` | StatsRepo (DAO) skeleton | Matches `get_recent_stats`, `get_session_list` |
| `services/__init__.py` | Package init | — |
| `services/routine_service.py` | RoutineService skeleton | Matches `generate_routine` (business logic above DAOs) |

**dataclass vs DAO distinction:**
- **dataclass** (`models.py`): The **shape** of data — what fields exist. Knows nothing about SQL.
- **DAO** (`repositories/*.py`): The **read/write** of data — hides SQL and returns dataclass objects. Business code only sees dataclasses.
- **Service** (`services/*.py`): **Business logic** combining multiple DAOs (e.g. `generate_routine` combines UserProfile + DailyLog + ExerciseLibrary).

**What "skeleton" means:**
Function signature + docstring + `raise NotImplementedError`. SQL implementations will be filled in after the 5/17 meeting once interfaces are confirmed.

---

### 7. Pending Decisions (5/17 Team Meeting)

| # | Item | Options | Notes |
|---|---|---|---|
| 1 | Remove `office` from `Scene` | Keep / Remove | Whether to keep office scenario. v2 keeps for now |
| 2 | Keep `outdoor_hours` | Keep / Remove | INPUT.md requires; commit `a625d30` removed. v2 keeps for now |
| 3 | `mental_condition_score` range | `0~10` vs `1~10` | Team `0~10` / INPUT.md `1~10`. v2 uses `0~10` |
| 4 | Remove `Workout_History.is_completed` | Keep (current) / Merge into `status` | v2 keeps |
| 5 | External exercise library choice | yuhonas/free-exercise-db / wger / other | — |
| 6 | Align `Exercise_Library` with external library | Add force / mechanic / primary_muscle / secondary_muscle / images? | After library selection |
| 7 | Expand fitness test from 3 to 5+ exercises | 3 (current) / 5+ | INPUT.md says 3 |
| 8 | `job_type` "free-text other" handling | TEXT free input / `other` enum + separate detail column | INPUT.md 2-1 |

---

### 8. Scope of Impact

#### 8.1 Breaking Changes

| Item | Impact |
|---|---|
| Dropped `User_Profile.fitness_level` | Existing references will error |
| Dropped `Daily_Log.sleep_hours / mood_score / fatigue_score` | Same |

→ Before running `schema_v2.sql`, audit and update all code referencing these columns.

#### 8.2 Non-breaking (Additive)

| Item | Detail |
|---|---|
| New columns added | **13 total** (User_Profile 9 + Daily_Log 3 + Workout_History 1 + Exercise_Library 1) |
| New files added | **12** (CHANGELOG x2 + schema_v2 + models + repositories/* 7 + services/* 2) |
| `constants.py` additions | 3 new enums + GYM added to Scene + 10 new constants |

#### 8.3 Impact on Existing Code

| File | Impact |
|---|---|
| `schema.sql` (v1) | **Unchanged** — kept for reference |
| `triggers_and_indexes.sql` | No impact (doesn't reference dropped columns) |
| `seed_data.sql` | No impact (seeds only `Exercise_Library`, not Daily_Log/User_Profile) |
| `README.md` | **Update needed** (TODO) |
| `requirement_analysis.md` | **Update needed** (TODO) |
| `er_diagram.dbml` / `er_diagram.mermaid` | **Update needed** (TODO) |

---

### 9. Rollback Plan

**Premise**: If `schema_v2.sql` has **not** been executed, no rollback is needed (only file additions).

**If executed and rollback is needed:**

1. SQLite 3.51 supports `DROP COLUMN`, but **dropped data cannot be recovered**.
2. **Strongly recommended**: Back up the DB file immediately before running `schema_v2.sql`.
   ```bash
   cp linkup.db linkup.db.v1_backup_$(date +%Y%m%d_%H%M%S)
   ```
3. To restore: restore the backup + remove code referencing new columns.

---

### 10. Verification

**Before execution (Python import checks):**
- [ ] `python3 -c "import constants; print(list(constants.Goal))"` runs without error
- [ ] `python3 -c "import constants; print(list(constants.Equipment))"` runs without error
- [ ] `python3 -c "import models; print(models.UserProfile())"` runs without error
- [ ] `python3 -c "from repositories import db"` no import errors

**After execution (SQLite checks):**
- [ ] `sqlite3 linkup.db ".schema User_Profile"` shows 9 new columns, no `fitness_level`
- [ ] `sqlite3 linkup.db ".schema Daily_Log"` shows 3 new, 3 dropped
- [ ] `sqlite3 linkup.db ".schema Workout_History"` shows `status` column
- [ ] `sqlite3 linkup.db ".schema Exercise_Library"` shows `equipment` column
- [ ] `sqlite3 linkup.db "SELECT * FROM User_Profile;"` existing row (id=1) preserved

---

### 11. References

**In this repo:**
- [schema.sql](../schema.sql) — v1 schema
- [constants.py](../constants.py) — Enum definitions
- [requirement_analysis.md](../requirement_analysis.md) — Initial requirements analysis (needs update)

**Team-internal docs (not in repo — get from team channel):**
- `INPUT.md` — New scenario requirements (cited as "INPUT.md 2-2" etc. in this doc)
- `UI.md` — Per-screen DB Interface list

**External:**
- [yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db) — Candidate exercise library

---

## v1 — 2026-04-13 (current production)

- Initial schema ([commit 6da4672](https://github.com/Rulinye/Linkup_db_temp))
- 6 tables: `User_Profile` / `Exercise_Library` / `Daily_Log` / `Workout_Session` / `Workout_History` / `App_Settings`
- 3 triggers + 5 indexes
- Details: [schema.sql](../schema.sql), [er_diagram.dbml](../er_diagram.dbml)
