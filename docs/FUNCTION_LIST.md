# 함수 정리 (펑션 정리)

본 문서는 LinkUp 프로젝트의 **시스템 함수 목록**과 각 함수가 도출된 **비기능적 요구사항(NFR)** 매핑을 정리합니다.

- 작성: 딩정 (DB 담당)
- 날짜: 2026-05-17
- 상태: **초안** — 성용 검토 후 확정
- 구현 위치: [repositories/](../repositories/), [services/](../services/)
- 데이터 구조 (DTO): [models.py](../models.py)

---

## 운영 모델 (요약)

- **저장**: 한 번 운동할 때마다 `Workout_Session` 한 행 생성 (chunk 단위)
- **표시**: 일별 집계 (SUM, GROUP BY date)
- **알고리즘**: 사용자는 「하루 목표 분」만 설정. routine 은 남은 분 (= 목표 − 누적) 기준으로 자동 생성

---

## 함수 ↔ NFR 매핑표

| # | 클래스 | 함수 | 작용 | 비기능적 요구사항 (NFR) | 비고 |
|---|---|---|---|---|---|
| 1 | UserProfileRepo | `has_profile() -> bool` | 사용자 프로필 작성 여부 확인 | 사용성 (초기화 분기) | 첫 실행 분기 |
| 2 | UserProfileRepo | `get() -> Optional[UserProfile]` | 프로필 전체 조회 | 응답성 / 데이터 영속성 | - |
| 3 | UserProfileRepo | `save(profile) -> None` | 프로필 생성/수정 (UPSERT) | 데이터 영속성 / 데이터 무결성 | - |
| 4 | DailyLogRepo | `get(date) -> Optional[DailyLog]` | 특정 날짜 일일 로그 조회 | 응답성 | - |
| 5 | DailyLogRepo | `get_today() -> Optional[DailyLog]` | 오늘 로그 조회 (편의 함수) | 사용성 | - |
| 6 | DailyLogRepo | `upsert(log) -> None` | 일일 로그 생성/수정 | 데이터 영속성 | - |
| 7 | WorkoutSessionRepo | `start(date, scene, started_at) -> int` | chunk 세션 시작 (session_id 반환) | 데이터 영속성 / 응답성 | - |
| 8 | WorkoutSessionRepo | `end(session_id, ended_at, …) -> None` | chunk 세션 종료 (TRG-2 가 duration 자동 계산) | 데이터 영속성 / 정확성 | - |
| 9 | WorkoutSessionRepo | `get(session_id) -> Optional[WorkoutSession]` | 특정 세션 조회 | 응답성 | - |
| 10 | WorkoutSessionRepo | `list_by_date(date) -> List[WorkoutSession]` | 특정 날짜의 모든 chunk 세션 시간순 목록 | 응답성 / 사용성 | 「10:00 5분, 13:00 10분」 표시용 |
| 11 | WorkoutHistoryRepo | `create(history) -> int` | 한 동작 수행 결과 기록 | 데이터 영속성 | - |
| 12 | WorkoutHistoryRepo | `update_status(history_id, status, …) -> None` | 동작 상태 업데이트 (완료/건너뜀/중단) | 데이터 무결성 / 사용성 | INPUT.md 5 의 일시정지/제외/그만두기 |
| 13 | WorkoutHistoryRepo | `list_by_session(session_id) -> List[WorkoutHistory]` | 한 세션의 모든 동작 기록 조회 | 응답성 | - |
| 14 | ExerciseLibraryRepo | `get(ex_id) -> Optional[ExerciseLibraryItem]` | 운동 동작 1건 조회 | 응답성 | - |
| 15 | ExerciseLibraryRepo | `get_modified(ex_id) -> Optional[ExerciseLibraryItem]` | 「너무 어려워요」 시 더 쉬운 대체 동작 조회 | 사용성 / 개인화 | INPUT.md 5 |
| 16 | ExerciseLibraryRepo | `list_all() -> List[ExerciseLibraryItem]` | 전체 동작 목록 | 응답성 | - |
| 17 | ExerciseLibraryRepo | `query(category, scene, max_difficulty, avoid_body_parts) -> List` | routine 알고리즘용 필터 조회 | 개인화 / 응답성 | - |
| 18 | StatsRepo | `recent_stats(days=7) -> RecentStats` | 최근 N일 통계 (완료율 / 연속일수) | 사용성 / 정확성 | 완료 = 「하루 누적 분 ≥ 목표」 |
| 19 | StatsRepo | `daily_history(limit=50) -> List[DailyHistorySummary]` | 과거 일별 운동 요약 목록 | 응답성 / 사용성 | History 화면 |
| 20 | StatsRepo | `daily_total_minutes(date) -> int` | 특정 날짜의 누적 운동 분 | 정확성 / 사용성 | - |
| 21 | StatsRepo | `daily_goal_met(date) -> bool` | 특정 날짜 목표 달성 여부 | 정확성 / 사용성 | - |
| 22 | StatsRepo | `list_today_chunks(date) -> List[WorkoutSession]` | 오늘 모든 chunk 시간순 (Dashboard 용) | 사용성 | 「10:00 5분」 표시 |
| 23 | AppSettingsRepo | `get(key) -> Optional[str]` | key/value 조회 (raw) | 응답성 | - |
| 24 | AppSettingsRepo | `set(key, value) -> None` | key/value UPSERT (raw) | 데이터 영속성 | - |
| 25 | AppSettingsRepo | `is_onboarding_completed() -> bool` | onboarding 완료 여부 (편의) | 사용성 | - |
| 26 | AppSettingsRepo | `mark_onboarding_completed() -> None` | onboarding 완료 표시 | 데이터 영속성 | - |
| 27 | AppSettingsRepo | `get_theme() -> str` | 현재 테마 조회 (편의) | 사용성 | - |
| 28 | AppSettingsRepo | `get_language() -> str` | 현재 언어 조회 (편의) | 사용성 | - |
| 29 | AppSettingsRepo | `db_version() -> str` | 현재 DB 스키마 버전 | 유지보수성 | - |
| 30 | RoutineService | `generate(date) -> List[ExerciseLibraryItem]` | 오늘 남은 분에 맞춰 routine 생성 (사용자 입력 없이 daily_remaining 기준 자동 계산) | 개인화 / 응답성 | - |
| 31 | RoutineService | `get_daily_remaining(date) -> int` | 오늘 목표까지 남은 분 | 사용성 / 정확성 | - |

총: **31개 함수**

---

## NFR 분류별 정리 (역방향)

| NFR | 이 NFR 때문에 생긴 함수들 |
|---|---|
| **사용성 (Usability)** | `has_profile`, `get_today`, `update_status`, `get_modified`, `recent_stats`, `daily_total_minutes`, `daily_goal_met`, `list_today_chunks`, `list_by_date`, `daily_history`, `get_daily_remaining`, `is_onboarding_completed`, `get_theme`, `get_language` |
| **데이터 영속성 (Persistence)** | `save`, `upsert`, `start`, `end`, `create`, `AppSettings.set`, `mark_onboarding_completed` |
| **데이터 무결성 (Integrity)** | `save`, `update_status` |
| **응답성 (Responsiveness)** | `get`, `get_today`, `list_*`, `query`, `start`, `generate`, `AppSettings.get` 등 거의 모든 read 함수 |
| **개인화 (Personalization)** | `query`, `generate`, `get_modified` |
| **정확성 (Accuracy)** | `end` (TRG-2 자동 계산), `recent_stats`, `daily_total_minutes`, `daily_goal_met`, `get_daily_remaining` |
| **유지보수성 (Maintainability)** | `db_version` |

---

## 미결정 (다음 회의 또는 개발 진입 시 결정)

DAO 시그니처에 영향 가능한 항목:

1. `Scene` 에서 `office` 삭제 여부 → `query(scene=...)` 의 enum 값 변동
2. `outdoor_hours` 필드 유지 여부 → `DailyLog` DTO 필드 변동
3. `mental_condition_score` 범위 (0~10 vs 1~10) → 검증 로직만 영향, 시그니처 불변
4. `is_completed` 컬럼 삭제 여부 → DAO 내부 동기화 로직 영향, 시그니처 불변
5. 외부 운동 라이브러리 선정 → `ExerciseLibraryRepo` import 스크립트 영향
6. 체력 측정 동작 3개 → 5개 확장 → `UserProfile` 필드만 추가, 시그니처 불변
7. `job_type` 자유 입력 처리 → `UserProfile` 필드만 추가, 시그니처 불변

대부분 **DTO 필드 차원**이므로 본 함수 정리표에는 영향 없음.

---

## 참고

- 변경 이력: [CHANGELOG_KOR.md](CHANGELOG_KOR.md)
