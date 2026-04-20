# My Brain — Wiki Schema

> 이 파일은 LLM이 읽는 규칙서다. 절대 수정하지 말 것.

## 목적

Claude와 나누는 모든 업무 대화, 생성된 문서, 미팅 내용을 누적/정제해서
다음 세션이 더 깊어지도록 만드는 개인 지식 베이스.

**메인 프로젝트:**
- **STEADY**: 한국 스포츠웨어 브랜드 창업
- **월가세교역**: 한국 화장품 일본 유통 무역상사 (현재 딘토 계약해지 분쟁 진행 중)

---

## Vault 구조

```
my-brain/
├── CLAUDE.md
├── raw/                       # 원본 — 절대 수정 금지
│   ├── inbox/                 # 미처리 대기열 (처리 후 비워야 정상)
│   │   ├── meetings/          # 클로바노트 export 등 회의록 투하
│   │   ├── documents/         # 계약서, 외부 문서 텍스트화 등
│   │   └── clips/             # 웹 스크랩, 이메일 등
│   ├── sessions/              # Claude 세션 자동 캡처 (SessionEnd 훅)
│   ├── meetings/              # 컴파일 완료된 회의록 보관
│   └── documents/             # 컴파일 완료된 문서 보관
└── wiki/
    ├── index.md               # 마스터 카탈로그 (L0, 항상 로드) — status:archived 항목 제외
    ├── log.md                 # 활동 로그 (append-only)
    ├── people/
    ├── companies/
    ├── deals/
    ├── legal/                 # 법적 사안 (분쟁/계약/법무)
    ├── projects/
    ├── decisions/
    ├── insights/
    └── documents/
```

---

## 토큰 로딩 전략 (L0-L3)

| 레벨 | 무엇 | 언제 |
|---|---|---|
| L0 | `wiki/index.md` | 항상 — 세션 시작 시 자동 주입 |
| L1 | 관련 project/deal/legal 페이지 | 현재 업무 맥락 파악 시. **active 프로젝트는 session-start 훅에서 최근 3개 자동 pull (updated 순, ≤4K 토큰)** |
| L2 | frontmatter만 grep | 검색/탐색 시 |
| L3 | 특정 페이지 full read | 깊이 있는 작업 필요 시만 |

**index.md 상한 정책**: 섹션당 최대 30행. 초과 시 LINT가 status=dormant 항목을 `wiki/index-archive.md`로 이동.

**Archive 배제 정책**: `status: archived` 또는 `status: closed` 페이지는 index.md에 포함하지 않음. L0 로딩에서 제외하여 노이즈 차단. 필요 시 L3에서 직접 읽기.

---

## Frontmatter 규약

### people/
```yaml
---
title: "이름"
type: person
role: investor | c-level | designer | manufacturer | influencer | brand-partner | jp-buyer | legal | other
project: [STEADY, 월가세교역]
company: [[companies/회사명]]
last_contact: YYYY-MM-DD
canonical_fields: [role, company, last_contact, status]  # C2 canonical source
status: active | dormant | closed | archived
summary: "한 줄 요약 (200자 이하)"
---
```

**Reading 섹션** — `people/` 페이지 본문에 추가 (V2 합의 2026-04-20):

```markdown
## 관찰 기록 (Reading)
> [!mirror] canonical: 각 프로젝트 Stance Log의 해당 항목

- "발언/행동 관찰 내용" (YYYY-MM-DD) → [[projects/관련프로젝트]] 참조
```

### companies/
```yaml
---
title: "회사명"
type: company
category: kr-brand | jp-buyer | manufacturer | agency | legal-firm | investor | other
project: [STEADY, 월가세교역]
status: active | negotiating | dispute | closed | archived
contact: [[people/주담당자]]
parent_company: [[companies/모기업]]  # optional — 자회사일 때만
canonical_fields: [category, status, contact, parent_company, summary]  # C2 canonical source
summary: "한 줄 요약 (200자 이하)"
---
```

### deals/
```yaml
---
title: "거래명"
type: deal
deal_type: investment | contract | partnership | vendor | dispute
project: [STEADY]
counterparty: [[companies/회사명]]       # 주 거래 상대 (요약 표시용)
parties: [[companies/A]], [[people/X]]  # 계약 당사자 전체 — C1 역참조 강제 (필수)
canonical_fields: [deal_type, status, parties, started]  # C2 canonical source
status: active | negotiating | resolved | closed | archived
started: YYYY-MM-DD
summary: "한 줄 요약 (200자 이하)"
---
```

### legal/  ← 법적 사안 전용
```yaml
---
title: "딘토 계약해지 분쟁"
type: legal-matter
matter_type: contract-termination | ip-dispute | labor | tax | other
project: [월가세교역]
counterparty: [[companies/딘토]]
parties: [[companies/A]], [[companies/B]]  # 전 당사자 — C1 역참조 강제 (필수)
our_counsel: [[people/변호사명]]
canonical_fields: [status, next_deadline, next_action, parties, our_counsel]  # C2 canonical source
status: pre-litigation | negotiating | filed | mediation | judgment | closed | archived | precedent
# archived: 종결 후 보관. precedent: 판례/참조 가치 있는 종결 건 (index.md 유지 예외)
next_deadline: YYYY-MM-DD
next_action: "다음에 해야 할 것"
started: YYYY-MM-DD
summary: "한 줄 요약 (200자 이하)"
---
```

### projects/
```yaml
---
title: "STEADY"
type: project
status: active | paused | closed | archived
stage: concept | discovery | analysis | design | draft | negotiation | production | launch | operation
project_type: ops | product-log | infra-build | report | poc  # D1b 합의 (2026-04-19) — 관찰 계측기. 3개월 후 enum 재정의.
entity: [[companies/회사명]]              # 소속 법인 — C1 역참조 강제 (필수). solo_project=true면 생략
solo_project: true                        # optional — 법인 없는 개인 PoC일 때만
canonical_fields: [stage, status, entity, project_type, updated]  # C2 canonical source
updated: YYYY-MM-DD
summary: "한 줄 요약 (200자 이하)"
---
```

**Stance Log** — `status: active` 프로젝트 페이지에 아래 섹션 추가 (V1 합의 2026-04-20):

```markdown
## 입장 변화 로그 (Stance Log)

### YYYY-MM-DD | [입장 주제]
**원래 입장**: [이전까지 믿었던 것]
**도전받은 지점**: [무엇이 흔들었나 — 사람 발언/데이터/직관]
**조정된 입장**: [지금 믿는 것]  ← claim (근거 명시)
**읽은 신호**: [영향 준 인물·상황 단서]  ← inference 가능 (추론임을 명시)
**아직 불확실한 것**: [다음 세션 검증 가설]
ref: [[raw/sessions/파일명]]
```

### decisions/
```yaml
---
title: "결정사항 제목"
type: decision
project: [STEADY, 월가세교역]
date: YYYY-MM-DD
status: confirmed | pending | revised | obsolete | archived
source: [[raw/sessions/파일명]]
supersedes: [[decisions/이전결정]]
tension: true                       # optional — 미결 전략 긴장 마킹 (V3 합의 2026-04-20)
revisit_trigger: "조건 또는 날짜"   # optional — 재검토 트리거
canonical_fields: [status, supersedes]  # C2 canonical source
summary: "한 줄 요약 (200자 이하)"
---
```

### insights/
```yaml
---
title: "인사이트 제목"
type: insight
project: [STEADY, 월가세교역]
source: [[raw/sessions/파일명]]
date: YYYY-MM-DD
status: active | archived
canonical_fields: [status, source]  # C2 canonical source
tags: []
summary: "한 줄 요약 (200자 이하)"
---
```

### documents/
```yaml
---
title: "문서 제목"
type: document
subtype: proposal | contract           # D2b 필수 (2026-04-19 Gemini A안)
project: [STEADY]
version: v1
status: active | archived
created: YYYY-MM-DD
updated: YYYY-MM-DD
location: [[raw/documents/파일명]]  # optional — 외부 파일 있을 때만. wiki 내부 작성 전문도 허용
canonical_fields: [version, status, location, subtype]  # C2 canonical source
summary: "한 줄 요약 (200자 이하)"

# subtype=proposal 필수 추가 필드:
audience: [[people/수신자1]], [[people/수신자2]]
round: 1 | 2 | 3 | final
feedback_status: pending | received | incorporated

# subtype=contract 필수 추가 필드:
# parties: [[companies/A]], [[people/X]]
# jurisdiction: "서울중앙지법" | "도쿄" | ...
# effective_date: YYYY-MM-DD
# expiry_date: YYYY-MM-DD | null
---
```

---

## 트리거 우선순위 (충돌 방지)

모호한 "정리해줘" 단독 발화 시 아래 순서로 판단:

| 발화 패턴 | 실행 Op |
|---|---|
| "세션 정리" / "오늘 정리" / "세션 컴파일" | SESSION-COMPILE |
| "미팅 정리" + (회의록 텍스트 첨부 OR raw/inbox/meetings/ 비어있지 않음) | INGEST |
| "wiki 점검" / "orphan 확인" | LINT |
| "[이름/주제] 브리핑" / "미팅 준비" | BRIEF |
| 그 외 "정리해줘" 단독 | Claude가 선택지 제시 |

---

## Operations

### BOOTSTRAP — 최초 1회 실행 (vault 초기화)

트리거: "wiki 초기화해줘", "처음 시작하자"

```
1. 사용자에게 다음을 순서대로 요청:
   a. STEADY 현재 상태 (단계, 팀, 주요 파트너 3-5개)
   b. 월가세교역 현재 유통 브랜드, 주요 일본 채널
   c. 딘토 분쟁 현재 상태 요약
   d. 자주 만나는 사람 5-10명 (이름, 역할, 소속)
2. 응답 기반으로:
   - wiki/projects/ 양쪽 현황판 초기화
   - wiki/legal/dinto-dispute-2026.md 생성
   - wiki/people/ + wiki/companies/ 초기 seed 생성
3. wiki/index.md 갱신
4. wiki/log.md append:
   ## [YYYY-MM-DD] bootstrap | 초기 wiki 생성 완료
```

---

### SESSION-COMPILE — Claude 세션 후 실행

트리거: "오늘 세션 정리해줘", "세션 컴파일해줘"

```
1. raw/sessions/ 에서 compiled: false 인 파일 목록 확인
2. 처리 전 사용자에게 확인:
   - 처리할 세션 파일 N개 목록
   - 새로 생성될 wiki 페이지 예상 목록
   - 업데이트될 기존 페이지 예상 목록
   → 사용자 승인 후 진행
3. 각 세션에서 추출:
   - 주요 결정사항 → decisions/ (기존 결정과 충돌 시 [!warning])
   - 새로운 인사이트 → insights/
   - 생성된 문서 → documents/ 인덱스
   - 언급된 사람 → people/ 생성/업데이트
   - 언급된 회사 → companies/ 생성/업데이트
   - 법적 사안 진전 → legal/ 업데이트
   - 프로젝트 현황 변화 → projects/ 타임라인에 append
   - [사업 대화 감지 — V4 합의 2026-04-20] people/·deals/·legal/ 언급이 다수이고 세션이 장시간(30턴+)인 경우:
     → 사용자에게 확인: "이 세션에 입장 변화가 있었나요? Stance Log 기록할까요?"
     → 확인 시: 해당 projects/ 페이지의 ## 입장 변화 로그 섹션에 append
     → 인물 새 관찰 감지 시: 해당 people/ 페이지의 ## 관찰 기록 섹션에 append (inference 명시)
4. 처리 완료한 세션 파일의 frontmatter를 compiled: true 로 수정
5. INDEX-REFRESH 호출 (변경 페이지 ≤3개면 Tier-A, ≥4개면 Tier-B 자동 선택)
6. wiki/log.md append:
   ## [YYYY-MM-DD] session-compile | [처리된 파일 수]개, [생성/업데이트된 페이지 요약]
```

---

### INGEST — 미팅 회의록 정리

트리거: "미팅 정리해줘" + 회의록 첨부 또는 raw/inbox/meetings/ 에 파일 존재 시

```
1. 입력 소스 확인:
   a. 회의록 텍스트 직접 첨부 → raw/inbox/meetings/YYYY-MM-DD_이름.md 에 임시 저장
   b. raw/inbox/meetings/ 에 파일이 이미 있으면 그대로 사용
2. 처리 전 사용자에게 확인:
   - 처리할 파일 목록 (inbox 파일 수 포함)
   - 새로 생성할 wiki 페이지 목록
   - 업데이트할 기존 페이지 목록 (entity resolution 포함)
   - 모호한 인물/회사 → "기존 [[hong-gil-dong]]과 동일 인물인가요?" 질문
   → 사용자 승인 후 진행
3. people/ 생성/업데이트
4. companies/ 생성/업데이트
5. deals/ or legal/ 업데이트 (해당 시)
6. projects/ 타임라인에 관련 내용 append
7. 처리 완료 후: raw/inbox/meetings/ 파일을 raw/meetings/YYYY-MM-DD_이름.md 로 이동
8. INDEX-REFRESH 호출 (변경 페이지 ≤3개면 Tier-A, ≥4개면 Tier-B 자동 선택)
9. wiki/log.md append
```

---

### BRIEF — 미팅/업무 전 브리핑

트리거: "[이름/주제] 브리핑해줘", "미팅 준비해줘"

```
1. wiki/index.md 에서 관련 항목 파악 (L0) — status:archived 제외
2. 관련 people/ + companies/ + deals/ + legal/ 읽기 (L1-L2)
2-1. index.md에서 찾지 못한 경우 OR 오랜만에 연락 온 entity (last_contact gap 6개월+) 감지 시:
     → wiki/ 디렉토리 직접 grep으로 archived 페이지까지 포함해서 재검색 (--include-archive)
3. 해당 데이터 없으면: raw/meetings/, raw/sessions/ 직접 검색 후 임시 브리프 생성
4. 출력:
   - 이 사람/주제가 누구/무엇인지 (archived 데이터 참조 시 명시)
   - 마지막 접촉 이후 변화
   - 현재 진행 중인 deal/legal 상태
   - 주의사항 및 성향 메모
   - 오늘 다룰 추천 아젠다
5. wiki에 없는 중요 정보 발견 시 INGEST 제안
```

---

### QUERY — 질문 답변

트리거: 자유 질문

```
1. wiki/index.md 에서 관련 페이지 파악 (L0) — 기본: status:archived 제외
1-1. 과거 회고 질문 ("예전에", "지난번에", "언제였지" 등) 또는 "--include-archive" 명시 시:
     → wiki/ 디렉토리 직접 grep으로 archived 페이지까지 포함해서 검색
2. 관련 페이지 읽기 (1-hop wikilink까지, 2-hop 금지)
3. 시간축 질문("지난달에", "작년에" 등) 감지 시:
   → wiki/log.md 해당 기간 확인 + 관련 raw/sessions/ 보조 검색
4. [[wikilink]] 인용으로 답변 (archived 페이지 참조 시 "[보관됨]" 표시)
5. 재사용 가치 있는 답변은 insights/ 저장 제안
```

---

### LINT — 정기 점검

트리거: "wiki 점검해줘", "orphan 확인해줘"

```
점검 항목:

[Index Drift]
- index.md 행 vs 실제 wiki/ 파일 1:1 매칭 — index에 있는데 파일 없거나, 파일 있는데 index 누락
- status: archived/closed 페이지가 index.md에 남아있으면 제거
- "_아직 없음_" 같은 placeholder 행 감지 및 보고

[Orphan & Links]
- Orphan 페이지 (인바운드 링크 0개)
- 깨진 wikilink (대상 파일 존재하지 않음)
- **인바운드 0 companies/ (C1 역참조 SPOF 검증)**: 모든 companies/*.md는 어딘가에서 wikilink 참조돼야 함. 참조 0건이면 drift 후보로 경고.
- **projects/ entity 누락 (C1)**: `entity:` 필드 없고 `solo_project: true`도 없으면 경고.
- **deals/ parties 누락 (C1)**: `parties:` 필드 없으면 경고.
- **legal/ parties 누락 (C1)**: `parties:` 필드 없으면 경고.

[Canonical Drift] — C2 canonical source 규약 검증
- canonical_fields에 선언된 필드가 동일 이름·값으로 다른 페이지 frontmatter 또는 본문 표에 나타나는 경우 검출
- mirror 콜아웃(`> [!mirror] canonical: [[source-page]]`) 없는 중복 표기 → 경고
- canonical_fields 누락된 entity 페이지(type별 기본값 부재) → 경고

[Documents KPI — Gemini A안 hard-stop]
상태 파일: `.omc/state/documents-lint-status.json` — LINT가 매번 갱신.
검사 규칙:
- `subtype` 필드 누락된 documents → 경고
- `subtype=proposal`인데 `audience`·`round`·`feedback_status` 중 하나라도 누락 → 경고
- `subtype=contract`인데 `parties`·`jurisdiction`·`effective_date` 중 하나라도 누락 → 경고
- 동일 title keyword (단어 단위 교집합 ≥2개)가 insights/와 documents/ 양쪽에 존재 → 중복 후보 카운트

KPI 측정:
- `search_fail_rate` = `wiki/documents-events.md`에서 `search-fail` event가 ≥2회 기록된 문서 수 / 전체 documents 수
- `duplicate_rate` = 중복 후보 쌍 수 / 전체 documents 수
- `contract_missing_effective_date_rate` = subtype=contract 중 effective_date 비어있는 수 / subtype=contract 전체
- `confusion_events` = `wiki/documents-events.md`의 `confusion` event 누적 카운트

Hard-stop 임계값 (Gemini A안 2026-04-19):
- `search_fail_rate > 0.20` → hard_stop=true
- `duplicate_rate > 0.15` → hard_stop=true
- `contract_missing_effective_date_rate > 0` → hard_stop=true
- `confusion_events >= 1` → hard_stop=true (즉시 발동)

Hard-stop 발동 시 LINT가 `documents-lint-status.json`에 `hard_stop: true` + `hard_stop_reason` + `schema_review_required_by` (금일+14일) 기록. session-start 훅이 해당 상태를 읽어 L0에 강력 경고 주입. 해제 조건: `wiki/decisions/documents-schema-review-YYYY-MM-DD.md` 신규 작성 + LINT 재실행 → status 리셋.

[Frontmatter Quality]
- frontmatter 누락/불완전 (title, type, status, summary 필수 필드 확인)
- type 값이 해당 디렉토리와 불일치 (예: people/에 type: project)
- status 값이 enum 외 자유서술 (각 타입별 허용 값 기준)
- project 필드가 배열 형식이 아님
- summary 200자 초과
- source 필드가 wikilink 형식 아님 (decisions/insights)

[Stale Content] — status=archived 페이지는 이 섹션 검사 제외
- status=active people 중 last_contact 3개월 이상
- projects/ 중 updated 60일 이상 + status=active → stale 경고
- decisions/ 중 status=pending 30일 이상 → 미결 경고
- legal/ 중 next_deadline 7일 이내 → 긴급 플래그
- deals/ 중 status=negotiating이면서 started 30일 이상 → stalled 경보

[Archive Candidates] — 사용자 승인 후 status→archived 전이
- deals/ 중 status=resolved/closed 60일 이상 → archive 후보
- projects/ 중 status=closed 30일 이상 → archive 후보
- people/ 중 status=closed → archive 후보
- decisions/ 중 status=obsolete → archive 후보
- legal/ 중 status=closed AND next_action 없음 → precedent 또는 archived 검토
- 후보 목록 사용자에게 제시 → 승인 시 frontmatter status 변경 + index.md 제거

[Inbox & Sessions]
- raw/inbox/ 파일 수 카운트 → 미처리 항목 보고
- compiled: false 세션 5개 이상 → SESSION-COMPILE 권장

[Index 용량]
- index.md 섹션당 30행 초과 → LINT가 last_contact/updated 기준 오래된 항목부터 index-archive.md로 이동 (물리 파일 이동 아님, index 행만)
- dormant는 frontmatter status 값이 아님 — LINT가 런타임으로 판정 (last_contact 3개월+ 또는 updated 60일+)
- INDEX-REFRESH Tier-B 호출 (전체 재빌드)

- log.md append: ## [YYYY-MM-DD] lint | [발견 이슈 요약]
```

---

### INBOX-DRAIN — inbox 전체 처리

트리거: "inbox 처리해줘", "밀린 거 처리해줘", raw/inbox/ 에 파일 존재 + 사용자 요청

```
1. raw/inbox/ 하위 전체 파일 목록 확인 (meetings/documents/clips 포함)
2. 사용자에게 처리 계획 확인:
   - 처리할 파일 목록 + 예상 분류 (meetings → INGEST, documents → wiki/documents, clips → insights 또는 INGEST)
   → 사용자 승인 후 진행
3. meetings/ → INGEST op와 동일한 흐름으로 처리
4. documents/ → wiki/documents/ 인덱스에 등록 + raw/documents/ 로 이동
5. clips/ → 내용 검토 후 관련 wiki 페이지에 append 또는 insights/ 신규 생성
6. 처리 완료 파일 inbox에서 해당 보관소로 이동
7. INDEX-REFRESH 호출
8. wiki/log.md append
```

---

### INDEX-REFRESH — index.md 효율 갱신

트리거: SESSION-COMPILE/INGEST 종료 시 자동 (Tier-A), LINT 종료 시 자동 (Tier-B)
트리거: "인덱스 재빌드해줘", "index 다시 만들어줘" → Tier-B 강제 실행

**"변경 페이지" 카운트 기준**: 파일 생성 +1, 내용 수정 +1, status 변경(active↔archived) +1. 파일 삭제는 카운트 안 함 (Tier-A step 2에서 자동 처리).

**index-archive.md 포맷**:
- 위치: wiki/index-archive.md
- 구조: index.md와 동일한 테이블 포맷, 섹션별 분류
- 추가 컬럼: `archived_date` (YYYY-MM-DD)
- 용도: index.md 30행 초과로 밀려난 항목 보관. 검색은 가능하나 L0 로딩 제외.
- 복원: LINT 또는 사용자 요청 시 index.md로 이동 가능

```
Tier-A (가벼운 패치) — 변경 페이지 ≤3개 시
  1. 변경된 페이지의 frontmatter에서 summary, status 추출
  2. status: archived/closed → index.md 해당 행 제거
  3. status: active (이전에 archived였던 경우) → index.md 해당 카테고리에 행 추가 (un-archive)
  4. 그 외 변경 → index.md 해당 행만 수정 (나머지 행 건드리지 않음)
  5. Last updated 날짜 갱신
  → 토큰: ~200

Tier-B (전체 재빌드) — LINT 시 또는 변경 페이지 ≥4개 시
  1. wiki/ 전체 스캔 (frontmatter grep)
  2. status: archived/closed 제외하고 카테고리별 재분류
  3. 섹션당 30행 초과 항목 → index-archive.md로 이동
  4. index.md 전체 재작성
  5. Last updated 갱신
  → 토큰: ~3,000
```

---

## 규칙

1. **raw/ 절대 수정 금지** — 원본 불변. 정정 필요 시 `원본파일.errata.md` 신규 작성
2. **LLM이 wiki 전부 작성** — 사람은 소스 제공 + 컴파일 승인만
3. **컴파일 전 사용자 확인 필수** — 모든 Op에서 처리 전 목록 보여주고 승인받기
4. **모든 내부 참조는 [[wikilink]]** — 따옴표 없이 작성 (Obsidian Graph 인식용)
5. **파일명**: `lowercase-hyphen.md` (홍길동 → `hong-gil-dong.md`, 한글명은 frontmatter `aliases:` 에 추가)
6. **날짜**: 항상 `YYYY-MM-DD`
7. **중복 금지**: 기존 페이지 업데이트 우선. 동명이인은 `kim-min-soo-2.md` 방식으로 suffix
8. **모순 발견 시**: `> [!warning]` 콜아웃. 해결은 사용자 승인 필수
9. **미결 사항**: `> [!question]` 콜아웃
10. **새 페이지 생성 후**: index.md 업데이트 + 관련 페이지 backlink 추가
11. **source 필드**: raw/sessions/ 파일의 실제 파일명 전체를 wikilink로 작성
12. **project 필드**: 항상 배열 형식 `[STEADY, 월가세교역]` — 단일값도 배열로
13. **Archive 규칙**: status를 archived로 변경 시 index.md에서 즉시 제거. 물리적 파일 이동 금지 (링크 깨짐 방지). LINT가 주기적으로 index 잔존 여부 검사. legal/는 status=precedent이면 index.md 유지.
14. **Inbox 규칙**: raw/inbox/ 는 항상 비어있어야 정상 상태. INGEST 완료 후 inbox 파일은 raw/meetings/ 또는 raw/documents/ 로 이동. LINT가 inbox 파일 수 보고.
15. **dormant 규칙**: dormant는 frontmatter status enum 값이 아님. LINT가 last_contact/updated 기준으로 런타임 판정하는 소프트 상태. index-archive.md 이동 기준으로만 사용.
16. **Un-archive 규칙**: archived 페이지를 active로 되돌릴 경우 status 변경 후 INDEX-REFRESH Tier-A 호출. index.md 해당 카테고리에 자동 재포함.
17. **역참조 규약 강제 (C1, [[decisions/consensus-mybrain-entity-model-2026-04-19]])**: 스키마 수준으로 다음 필수 — projects: `entity` 또는 `solo_project:true`, deals: `parties`, legal: `parties`, people: `company`(기존). Obsidian 그래프는 시각화 도구이며 의미적 보증 아님. LINT가 인바운드 0 companies 감지해 SPOF 차단.
18. **canonical source 규약 (C2)**: 각 entity 페이지의 `canonical_fields`에 명시된 필드는 해당 페이지가 유일한 수정 권한. 다른 페이지에 동일 정보 표기 시 `> [!mirror] canonical: [[source-page]]` 콜아웃 필수. LINT가 미마킹 중복을 검출. 타입별 기본 canonical_fields는 Frontmatter 규약 섹션 참조 — 페이지 단위 override 가능.
19. **documents subtype 규약 (D2b, [[decisions/consensus-mybrain-d1d2-resolution-2026-04-19]])**: `documents/` frontmatter에 `subtype: proposal | contract` 필수. subtype별 필수 추가 필드(proposal: audience·round·feedback_status / contract: parties·jurisdiction·effective_date·expiry_date) 누락 시 LINT 경고. policy subtype은 현재 미예정.
20. **documents KPI hard-stop (Gemini A안, 2026-04-19)**: 아래 KPI 임계값 초과 시 LINT가 hard_stop 발동 — `.omc/state/documents-lint-status.json`에 기록, session-start 훅이 L0에 경고 주입, 신규 documents 생성 차단. 해제: `wiki/decisions/documents-schema-review-YYYY-MM-DD.md` 작성 + LINT 재실행.
    - 재검색 실패율 > 20% (기록처: wiki/documents-events.md `search-fail` event)
    - insights-documents 중복률 > 15% (LINT title keyword 매칭 자동)
    - contract effective_date 누락률 > 0%
    - 의무/효력 혼동 이벤트 ≥ 1 (기록처: wiki/documents-events.md `confusion` event)
21. **documents 이벤트 기록 (Gemini KPI 계측 지원)**: 재검색 실패나 의무/효력 혼동 발생 시 `wiki/documents-events.md` append-only 로그에 `## [YYYY-MM-DD] <event_type> | [[대상 문서]] | 상세` 형식으로 기록. 이는 KPI 측정 소스이자 Gemini 원안의 "정식 계측" 요구 충족 수단.
