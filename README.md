# my-brain

Claude와 함께 쓰는 개인 지식 베이스(PKB) 템플릿.

미팅 회의록, 업무 결정사항, 프로젝트 현황을 Claude가 자동으로 정리하고 누적해준다.
다음 세션에서 "저번에 어떻게 됐더라?"를 물어보면 바로 답해준다.

---

## 구조

```
my-brain/
├── CLAUDE.md          ← 핵심. Claude가 읽는 운영 규칙서
├── wiki/              ← 정제된 지식 저장소
│   ├── index.md       ← 마스터 카탈로그 (Claude가 항상 읽음)
│   ├── log.md         ← 활동 로그 (append-only)
│   ├── people/        ← 사람
│   ├── companies/     ← 회사
│   ├── projects/      ← 프로젝트
│   ├── decisions/     ← 결정사항
│   ├── insights/      ← 인사이트
│   ├── deals/         ← 거래/계약
│   ├── legal/         ← 법적 사안
│   └── documents/     ← 문서 인덱스
└── raw/               ← 원본 데이터 (절대 수정 금지)
    ├── inbox/         ← 처리 대기열
    │   ├── meetings/  ← 회의록 투하 위치
    │   ├── documents/ ← 계약서 등 외부 문서
    │   └── clips/     ← 웹 스크랩, 이메일
    ├── sessions/      ← Claude 세션 자동 캡처
    ├── meetings/      ← 처리 완료된 회의록
    └── documents/     ← 처리 완료된 문서
```

---

## 설치 방법

### 1. 사전 준비

- **Node.js** 설치: https://nodejs.org (LTS 버전)
- **Anthropic API Key** 발급: https://console.anthropic.com

### 2. Claude Code 설치

터미널을 열고 실행:

```bash
npm install -g @anthropic-ai/claude-code
```

설치 확인:

```bash
claude --version
```

### 3. 이 레포 클론

```bash
git clone https://github.com/YOUR_REPO/my-brain.git
cd my-brain
```

### 4. API Key 설정

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export ANTHROPIC_API_KEY="sk-ant-..."
```

저장 후:

```bash
source ~/.zshrc
```

### 5. Session 훅 설정

Claude Code가 세션 시작/종료 시 자동으로 wiki context를 주입하도록 훅을 설정한다.

`~/.claude/settings.json` 파일을 열거나 생성:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cat ~/your-path/my-brain/wiki/index.md"
          }
        ]
      }
    ]
  }
}
```

> `~/your-path/my-brain` 부분을 실제 경로로 바꿔줘.

### 6. Claude Code로 my-brain 열기

```bash
cd ~/your-path/my-brain
claude
```

### 7. 초기화 (최초 1회)

Claude Code 안에서 입력:

```
wiki 초기화해줘
```

Claude가 질문을 몇 가지 던지고, 네 상황에 맞게 wiki를 자동으로 채워준다.

---

## 주요 명령어

Claude Code 안에서 자유롭게 말하면 된다.

| 명령 | 설명 |
|---|---|
| `wiki 초기화해줘` | 최초 1회. 내 상황 기반으로 vault 생성 |
| `미팅 정리해줘` + 회의록 붙여넣기 | 회의록 → wiki 자동 변환 |
| `오늘 세션 정리해줘` | 대화 내용 → wiki 누적 |
| `[이름] 브리핑해줘` | 특정 사람/주제 현황 요약 |
| `[프로젝트명] 현황 알려줘` | 프로젝트 상태 조회 |
| `wiki 점검해줘` | 깨진 링크, 누락 항목 검사 |

---

## 작동 원리

1. `CLAUDE.md` — Claude가 이 파일을 읽고 운영 규칙을 파악
2. `wiki/index.md` — 세션마다 자동 주입되는 마스터 카탈로그 (L0)
3. 나머지 wiki 페이지들 — 필요할 때만 읽음 (L1~L3, 토큰 절약)

Claude가 직접 파일을 쓰고, 너는 승인만 하면 된다.

---

## 팁

- **회의록은 raw/inbox/meetings/ 에 파일로 넣거나**, 그냥 텍스트를 Claude에게 붙여넣어도 됨
- **Obsidian** 앱으로 wiki 폴더를 열면 그래프 뷰로 연결 관계를 시각화할 수 있음 (선택사항)
- 민감한 정보(법적 분쟁, 계약 등)는 `review/consensus` 기능에 넣지 말 것
