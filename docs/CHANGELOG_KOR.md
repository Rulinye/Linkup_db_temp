# DB Schema 변경 이력 (한국어)

본 문서는 LinkUp 프로젝트의 DB schema 및 관련 코드 (constants / models / repositories) 변경 이력을 기록합니다.
영문판: [CHANGELOG_EN.md](CHANGELOG_EN.md)

작성 원칙:
- 모든 변경은 **사유**, **영향 범위**, **롤백 방안**을 포함해야 한다.
- 변경 사유의 출처 (INPUT.md / UI.md / 팀 회의 / 외부 라이브러리) 를 명시한다.
- 미결정 사항은 별도 섹션에 모아 다음 회의에서 확정한다.

---

## v2.2 — 2026-05-17 (계획중 / Planned, 미실행)

### 변경 배경

검토 피드백 반영. 「하루 목표 분」 방식보다 **「매번 사용자가 입력한 시간만큼 routine 생성 + 하루치는 단순 합산」** 이 회의 결정 「3~10분 쪼개서 합산」 의도에 더 부합한다고 판단.

### Schema 변경

| 테이블 | 변경 |
|---|---|
| `User_Profile` | **삭제** `daily_total_goal_min` (v2.1 에서 추가했던 컬럼) |

### Constants 변경

- **삭제**: `DAILY_GOAL_MIN`, `DAILY_GOAL_MAX`, `DAILY_GOAL_DEFAULT`

### DTO (`models.py`) 변경

- `UserProfile.daily_total_goal_min` **삭제**

### DAO / Service 변경

| 변경 | 내용 |
|---|---|
| `RoutineService.generate(date)` → `generate(date, available_min)` | 사용자가 매번 입력한 분 수를 받음 |
| `RoutineService.get_daily_remaining()` | **삭제** (daily goal 없음) |
| `StatsRepo.daily_goal_met()` | **삭제** (daily goal 없음) |
| `StatsRepo` `__init__` | `UserProfileRepo` 의존성 제거 (v2.1 fix 가 불필요해짐) |
| `RecentStats` | `completion_rate` → `active_days` 로 변경 (운동 한 적 있는 날 수) |
| `DailyHistorySummary` | `goal_met` 필드 삭제 |

함수 수: 31개 → **29개**.

### 영향 범위

- **파괴적**: `daily_total_goal_min` 컬럼 삭제 (v2.1 가 미실행이라 실제 데이터 없음, 영향 0)
- **비파괴적**: 위 외 전부 (SKELETON 단계)

### 롤백

`schema_v2.sql` 미실행 → 롤백 불필요.

---

## v2.1 — 2026-05-17 (계획중 / Planned, 미실행)

### 변경 배경

5/17 팀 회의 결과를 반영. 주요 결정 사항:
- 운동 기구 필요한 동작 전부 제외 (徒手 only)
- 「3~10분 chunk 로 쪼개서 누적 15~20분」 운동 모델
- 사용자가 매번 chunk 길이 입력하지 않음 — onboarding 에서 「하루 목표 분」만 설정, routine 은 daily_remaining 기준 자동 생성
- 「안전」 용어는 「부담 없는 / 최소한의 운동」 으로 대체 (문서 표현)
- 질병 분류 제거, 신체 부위 단위로만 운용 (기존 schema 그대로 호환)

### Schema 변경 (v2 대비 추가 변경)

| 테이블 | 변경 |
|---|---|
| `User_Profile` | **삭제** `preferred_duration_min` (v1 컬럼) |
| `User_Profile` | **추가** `daily_total_goal_min INTEGER DEFAULT 15 CHECK 5~60` |
| `Exercise_Library` | v2 의 `equipment` 컬럼 추가 **취소** |

### Constants 변경

- **삭제**: `Equipment` enum (10개 값)
- **삭제**: `Scene.GYM`
- **삭제**: `validate_equipment_list()`
- **유지**: `MENTAL_CONDITION_MIN/MAX`, `OUTDOOR_HOURS_MIN/MAX`, 기타
- **추가**: `DAILY_GOAL_MIN = 5`, `DAILY_GOAL_MAX = 60`, `DAILY_GOAL_DEFAULT = 15`

### DTO (`models.py`) 변경

- `UserProfile.available_equipment` **삭제**
- `UserProfile.preferred_duration_min` **삭제**
- `UserProfile.daily_total_goal_min` **추가** (기본값 15)
- `ExerciseLibraryItem.equipment` **삭제**

### DAO 변경

| 변경 | 내용 |
|---|---|
| `ExerciseLibraryRepo.query()` | `equipment_in` 파라미터 삭제 |
| `StatsRepo.session_list()` | → `daily_history()` 로 개명, `DailyHistorySummary` 반환 |
| `StatsRepo.recent_stats()` | 「완료」 정의 변경 (session 단위 → 일별 누적 분 ≥ 목표) |
| `StatsRepo` (신규) | `daily_total_minutes(date)` |
| `StatsRepo` (신규) | `daily_goal_met(date)` |
| `StatsRepo` (신규) | `list_today_chunks(date)` |
| `RoutineService.generate(date)` | 시그니처 유지. 내부에서 daily_remaining 계산 |
| `RoutineService` (신규) | `get_daily_remaining(date)` |
| **신규 클래스** `AppSettingsRepo` | 7개 메서드 (`get`/`set`/`is_onboarding_completed`/`mark_onboarding_completed`/`get_theme`/`get_language`/`db_version`) |

총 함수 수: **31개** (UserProfile 3 + DailyLog 3 + WorkoutSession 4 + WorkoutHistory 3 + ExerciseLibrary 4 + Stats 5 + AppSettings 7 + RoutineService 2).

### 신규 파일

- `docs/FUNCTION_LIST.md` — 함수 31개 + NFR 매핑표 (검토용)
- `repositories/app_settings_repo.py` — AppSettingsRepo 스켈레톤

### 영향 범위

- **파괴적**: `preferred_duration_min` 삭제 → 기존 코드 참조 시 에러 (v1 schema 사용 시점부터 누적된 데이터 손실)
- **비파괴적**: 신규 컬럼 / 신규 클래스 / 신규 함수 추가
- **문서**: README.md, requirement_analysis.md, er_diagram 갱신 필요 (TODO)

### 롤백

`schema_v2.sql` 실행 **전** 이면 롤백 불필요.
실행 후 롤백 필요 시 백업 파일 복원.

---

## v2 — 2026-05-16 (계획중 / Planned, 미실행)

### 1. 문서 정보

| 항목 | 값 |
|---|---|
| 상태 | **계획중 (Pending)** — `schema_v2.sql` 미실행 |
| 확정 예정일 | 2026-05-17 팀 회의 후 |
| 이전 버전 | v1 ([schema.sql](../schema.sql)) |
| 적용 명령 | `sqlite3 linkup.db < schema_v2.sql` (회의 후) |

### 2. 변경 배경

2026년 5월 개발 추진과 함께 다음 입력이 반영됨:

1. **INPUT.md** — 신규 시나리오 (직업/목표/기간/빈도/기구/통증/체력/알림/외부활동/스트레스)
2. **UI.md** — 화면별 DB Interface 목록 (DAO 설계의 근거)
3. **팀 회의 결정 사항** — 정신적 컨디션 통합, 서버/로그인 미사용, 기구 포함 (아래 § 3 인용)
4. **외부 운동 라이브러리 연동 준비** — yuhonas/free-exercise-db 등 검토 중

### 3. 팀 회의 결정 사항

- 서버/로그인 없음 → 현재 단일 사용자 로컬 SQLite 설계 그대로 유지 (변경 없음).
- 수면 + 기분 + 스트레스 → **단일 점수** `mental_condition_score` 0~10 (10=최상) 으로 통합.
- 기구 → `User_Profile.available_equipment` 컬럼 추가.

---

### 4. 변경 사항 상세

#### 4.1 `User_Profile` 테이블

**삭제 컬럼:**

| 컬럼 | 사유 |
|---|---|
| `fitness_level INTEGER 1~5` | 추상적 자가평가 → INPUT.md 2-7 의 구체적 3종 측정값 (`pushup_max`, `plank_max_sec`, `squat_max`) 으로 대체. 1~5 등급은 routine 알고리즘에서 측정값으로부터 현장 계산. |

**추가 컬럼:**

| 컬럼 | 타입 | 기본값 | CHECK | 출처 | 설명 |
|---|---|---|---|---|---|
| `avatar_path` | TEXT | NULL | — | INPUT.md 1-2 | 프로필 사진 로컬 파일 경로 (BLOB 미사용) |
| `goals` | TEXT | `''` | — | INPUT.md 2-2 | 운동 목표 CSV. `Goal` enum 값 사용. 예: `'muscle_gain,diet'` |
| `goal_duration_weeks` | INTEGER | NULL | 1~24 | INPUT.md 2-3 | 목표 기간 1~24주 |
| `weekly_frequency` | INTEGER | NULL | 1~7 | INPUT.md 2-4 | 주간 운동 빈도 1~7회 |
| `available_equipment` | TEXT | `''` | — | INPUT.md 2-8 | 보유 기구 CSV. `Equipment` enum 값 사용. 예: `'dumbbell,band'` |
| `notification_enabled` | INTEGER | `1` | 0 또는 1 | INPUT.md 2-9 | 알림 on/off. 0=꺼짐, 1=켜짐 |
| `pushup_max` | INTEGER | NULL | ≥ 0 | INPUT.md 2-7 | 팔굽혀펴기 최대 횟수. NULL = "잘 모르겠다" |
| `plank_max_sec` | INTEGER | NULL | ≥ 0 | INPUT.md 2-7 | 플랭크 최대 유지 시간 (초). NULL = "잘 모르겠다" |
| `squat_max` | INTEGER | NULL | ≥ 0 | INPUT.md 2-7 | 스쿼트 최대 횟수. NULL = "잘 모르겠다" |

**미변경 컬럼:**
`id`, `nickname`, `birth_year`, `height_cm`, `weight_kg`, `job_type`, `pain_points`, `preferred_duration_min`, `daily_step_goal`, `reminder_interval_min`, `created_at`, `updated_at`

#### 4.2 `Daily_Log` 테이블

**삭제 컬럼:**

| 컬럼 | 사유 |
|---|---|
| `sleep_hours REAL` | 팀 결정: `mental_condition_score` 에 통합 (UI 입력 없음) |
| `mood_score INTEGER 1~5` | 팀 결정: `mental_condition_score` 에 통합 |
| `fatigue_score INTEGER 1~10` | INPUT.md 3-2-2: 단일 점수 → 부위별 → `fatigue_by_part` 로 대체 |

**추가 컬럼:**

| 컬럼 | 타입 | 기본값 | CHECK | 출처 | 설명 |
|---|---|---|---|---|---|
| `mental_condition_score` | INTEGER | NULL | 0~10 | 팀 회의 | 정신적 컨디션 통합 점수. **10=최상** (수면+기분+스트레스 포함) |
| `outdoor_hours` | REAL | NULL | 0~16 | INPUT.md 3-2-1 | 외부활동 시간 0~16시간 |
| `fatigue_by_part` | TEXT | `'{}'` | — | INPUT.md 3-2-2 | 부위별 피로도 JSON. 예: `{"neck":7,"shoulder":3}` |

**`fatigue_by_part` JSON 규약:**
- key: `BodyPart` enum 값 (`neck`, `shoulder`, `lower_back` 등)
- value: 1~10 정수
- 통증 없는 부위는 key 자체를 생략 (sparse 형식)
- 빈 객체 `{}` = 모든 부위 피로 없음

**미변경 컬럼:**
`date`, `step_count`, `manual_scene`, `created_at`

#### 4.3 `Workout_History` 테이블

**추가 컬럼:**

| 컬럼 | 타입 | 기본값 | CHECK | 출처 | 설명 |
|---|---|---|---|---|---|
| `status` | TEXT | `'pending'` | enum | INPUT.md 5 | 동작 상태. `pending` / `completed` / `skipped` / `aborted` |

**status 의미:**
| 값 | 의미 | INPUT.md 5 대응 |
|---|---|---|
| `pending` | 아직 수행 안 함 (기본값) | 세션 시작 시 |
| `completed` | 정상 완료 | — |
| `skipped` | "현재 진행 중인 동작 제외" 로 건너뜀 | "현재 진행 중인 동작 제외" |
| `aborted` | "그만두기" 로 중단됨 | "그만두기" |

**기존 컬럼 `is_completed BOOLEAN` 처리:**
- 호환성 유지 위해 **삭제하지 않음**
- DAO 에서 `status = 'completed'` 와 자동 동기화
- 5/17 회의 후 삭제 검토 가능

**미변경 컬럼:**
`history_id`, `session_id`, `ex_id`, `seq_order`, `actual_sets`, `actual_duration_sec`, `is_completed`, `used_modified`, `feedback`, `pain_during`

#### 4.4 `Exercise_Library` 테이블

**추가 컬럼:**

| 컬럼 | 타입 | 기본값 | 출처 | 설명 |
|---|---|---|---|---|
| `equipment` | TEXT | `'none'` | INPUT.md 2-8 연동 | 사용 기구 (단일값). `Equipment` enum. `User_Profile.available_equipment` 와 필터링 매칭 |

**외부 라이브러리 연동 시 추가 검토 (5/17 회의 후 결정):**
- `force` TEXT — push / pull / static
- `mechanic` TEXT — compound / isolation
- `primary_muscle` TEXT — 현재 `target_muscle` 분리
- `secondary_muscle` TEXT — 현재 `target_muscle` 분리
- `images` TEXT — JSON 배열, 현재 `media_path` 단일에서 다중 지원

#### 4.5 `Workout_Session`, `App_Settings` 테이블

**변경 없음.**

---

### 5. constants.py 변경

**신규 Enum 추가:**

#### `Goal` (운동 목표, INPUT.md 2-2)
| value | label_ko |
|---|---|
| `muscle_gain` | 근육량 증가 |
| `diet` | 다이어트 |
| `lifestyle` | 생활 습관 개선 |
| `basic_fitness` | 기초 체력 증가 |
| `none` | 없음 |

#### `Equipment` (보유 기구, INPUT.md 2-8)
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

#### `SessionStatus` (동작 상태, INPUT.md 5)
| value | label_ko |
|---|---|
| `pending` | 대기 |
| `completed` | 완료 |
| `skipped` | 건너뜀 |
| `aborted` | 중단됨 |

**기존 Enum 변경:**

| Enum | 변경 |
|---|---|
| `Scene` | `gym` (`헬스장`) 추가. `office`, `home` 유지. ⚠️ `office` 삭제 여부는 5/17 회의에서 결정 |

**상수 추가:**
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

**상수 삭제:**
```python
FITNESS_LEVEL_MIN  # fitness_level 컬럼 삭제됨
FITNESS_LEVEL_MAX  # 동상
```

---

### 6. 신규 파일

| 파일 | 역할 | 비고 |
|---|---|---|
| `models.py` | 6개 테이블의 dataclass 정의 | 비즈니스 로직 ↔ DAO 사이의 데이터 컨테이너 |
| `schema_v2.sql` | v1 → v2 마이그레이션 스크립트 | **회의 후 실행** |
| `repositories/__init__.py` | 패키지 초기화 | — |
| `repositories/db.py` | SQLite 연결 헬퍼 | `get_connection()` 등 |
| `repositories/user_profile_repo.py` | UserProfileRepo (DAO) 스켈레톤 | UI.md 의 `has_user_profile`, `get_user_profile`, `save_user_profile` 대응 |
| `repositories/daily_log_repo.py` | DailyLogRepo (DAO) 스켈레톤 | `get_today_log`, `upsert_today_log` 대응 |
| `repositories/workout_session_repo.py` | WorkoutSessionRepo (DAO) 스켈레톤 | `start_session`, `end_session` 대응 |
| `repositories/workout_history_repo.py` | WorkoutHistoryRepo (DAO) 스켈레톤 | `record_history` 대응 |
| `repositories/exercise_library_repo.py` | ExerciseLibraryRepo (DAO) 스켈레톤 | `get_modified_exercise` 대응 |
| `repositories/stats_repo.py` | StatsRepo (DAO) 스켈레톤 | `get_recent_stats`, `get_session_list` 대응 |
| `services/__init__.py` | 패키지 초기화 | — |
| `services/routine_service.py` | RoutineService 스켈레톤 | `generate_routine` 대응 (DAO 위의 비즈니스 로직) |

**dataclass vs DAO 구분:**
- **dataclass** (`models.py`): 데이터의 **모양** — 어떤 필드가 있는지. SQL 모름.
- **DAO** (`repositories/*.py`): 데이터의 **읽기/쓰기** — SQL 을 숨기고 dataclass 를 반환. 비즈니스 로직은 dataclass 만 본다.
- **Service** (`services/*.py`): 여러 DAO 를 조합한 **비즈니스 로직** (예: `generate_routine` 은 UserProfile + DailyLog + ExerciseLibrary 를 조합).

**스켈레톤이란:**
함수 시그니처 + docstring + `raise NotImplementedError`. 5/17 회의에서 인터페이스 확정 후 SQL 구현 채울 예정.

---

### 7. 미결정 사항 (5/17 팀 회의)

| # | 항목 | 옵션 | 비고 |
|---|---|---|---|
| 1 | `Scene` 에서 `office` 삭제 여부 | 유지 / 삭제 | 사무실 시나리오 유지 여부. v2 는 일단 유지 |
| 2 | `outdoor_hours` 유지 여부 | 유지 / 삭제 | INPUT.md 는 요구, 이전 커밋 `a625d30` 은 outdoor 삭제. v2 는 일단 유지 |
| 3 | `mental_condition_score` 범위 | `0~10` vs `1~10` | 팀 회의 `0~10` / INPUT.md `1~10`. v2 는 `0~10` 채택 |
| 4 | `Workout_History.is_completed` 삭제 여부 | 유지 (현재) / `status` 로 통합 후 삭제 | v2 는 유지 |
| 5 | 외부 운동 라이브러리 선정 | yuhonas/free-exercise-db / wger / 기타 | — |
| 6 | `Exercise_Library` 외부 라이브러리 schema 정렬 | force / mechanic / primary_muscle / secondary_muscle / images 추가 여부 | 라이브러리 선정 후 결정 |
| 7 | 체력 측정 동작 수 확장 | 3개 (현재) / 5개 이상 | INPUT.md 는 3개 |
| 8 | `job_type` 의 "직접 입력" 처리 | TEXT 자유 입력 / `other` enum + 별도 detail 컬럼 | INPUT.md 2-1 |

---

### 8. 영향 범위

#### 8.1 파괴적 변경 (Breaking)

| 항목 | 영향 |
|---|---|
| `User_Profile.fitness_level` 삭제 | 기존 코드에서 참조 시 에러 |
| `Daily_Log.sleep_hours / mood_score / fatigue_score` 삭제 | 동상 |

→ schema_v2.sql 실행 전, 이 컬럼들을 참조하는 모든 코드를 확인 / 수정 필요.

#### 8.2 비파괴적 변경 (Additive)

| 항목 | 내용 |
|---|---|
| 신규 컬럼 추가 | 총 **13개** (User_Profile 9 + Daily_Log 3 + Workout_History 1 + Exercise_Library 1) |
| 신규 파일 추가 | **12개** (CHANGELOG x2 + schema_v2 + models + repositories/* 7 + services/* 2) |
| `constants.py` 추가 | 신규 Enum 3개 + Scene 에 GYM 추가 + 상수 10개 추가 |

#### 8.3 기존 코드 영향

| 파일 | 영향 |
|---|---|
| `schema.sql` (v1) | **미수정** — 참조용으로 유지 |
| `triggers_and_indexes.sql` | 영향 없음 (삭제된 컬럼 미참조) |
| `seed_data.sql` | 영향 없음 (`Exercise_Library` 만 seed, Daily_Log/User_Profile 미참조) |
| `README.md` | **업데이트 필요** (TODO) |
| `requirement_analysis.md` | **업데이트 필요** (TODO) |
| `er_diagram.dbml` / `er_diagram.mermaid` | **업데이트 필요** (TODO) |

---

### 9. 롤백 방안

**전제**: `schema_v2.sql` 실행 **전** 이면 롤백 불필요 (파일 추가만 되어 있는 상태).

**실행 후 롤백 필요 시:**

1. SQLite 3.51 은 `DROP COLUMN` 지원하지만, **삭제된 데이터는 복구 불가**.
2. **권장**: `schema_v2.sql` 실행 직전 DB 파일 백업.
   ```bash
   cp linkup.db linkup.db.v1_backup_$(date +%Y%m%d_%H%M%S)
   ```
3. 복원 시: 백업 파일 복원 + 신규 컬럼 참조 코드 제거.

---

### 10. 검증 방법

**실행 전 (Python import 검증):**
- [ ] `python3 -c "import constants; print(list(constants.Goal))"` 정상 출력
- [ ] `python3 -c "import constants; print(list(constants.Equipment))"` 정상 출력
- [ ] `python3 -c "import models; print(models.UserProfile())"` 정상 출력
- [ ] `python3 -c "from repositories import db"` import 에러 없음

**실행 후 (SQLite 검증):**
- [ ] `sqlite3 linkup.db ".schema User_Profile"` 신규 9개 컬럼 확인, `fitness_level` 부재 확인
- [ ] `sqlite3 linkup.db ".schema Daily_Log"` 신규 3개 / 삭제 3개 확인
- [ ] `sqlite3 linkup.db ".schema Workout_History"` `status` 컬럼 확인
- [ ] `sqlite3 linkup.db ".schema Exercise_Library"` `equipment` 컬럼 확인
- [ ] `sqlite3 linkup.db "SELECT * FROM User_Profile;"` 기존 데이터 (id=1) 보존 확인

---

### 11. 참조 문서

**저장소 내:**
- [schema.sql](../schema.sql) — v1 schema
- [constants.py](../constants.py) — Enum 정의
- [requirement_analysis.md](../requirement_analysis.md) — 초기 요구 분석 (업데이트 필요)

**팀 내부 문서 (저장소 외 — 팀 공유 채널에서 확인):**
- `INPUT.md` — 신규 시나리오 요구사항 (본 문서에서 "INPUT.md 2-2" 등으로 인용)
- `UI.md` — 화면별 DB Interface 목록

**외부:**
- [yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db) — 운동 라이브러리 후보

---

## v1 — 2026-04-13 (현재 운용)

- 최초 schema 작성 ([커밋 6da4672](https://github.com/Rulinye/Linkup_db_temp))
- 6개 테이블: `User_Profile` / `Exercise_Library` / `Daily_Log` / `Workout_Session` / `Workout_History` / `App_Settings`
- 3개 트리거 + 5개 인덱스
- 자세한 내용: [schema.sql](../schema.sql), [er_diagram.dbml](../er_diagram.dbml)
