#!/usr/bin/env python3
"""
SessionStart 훅 — wiki/index.md를 L0로 주입.
- compiled: false 파일 카운트로 pending 경고
- L1 Pull: status:active 프로젝트 최근 3개 자동 로드 (V5 합의 2026-04-20)
- cwd guard: resolve() 기반으로 엣지케이스 처리
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, date

BRAIN_DIR = Path.home() / "Documents" / "my-brain"
INDEX_FILE = BRAIN_DIR / "wiki" / "index.md"
SESSIONS_DIR = BRAIN_DIR / "raw" / "sessions"
PROJECTS_DIR = BRAIN_DIR / "wiki" / "projects"
DOCS_LINT_STATUS = BRAIN_DIR / ".omc" / "state" / "documents-lint-status.json"

L1_MAX_CHARS = 16_000   # ~4,000 토큰 상한
L1_MAX_FILES = 3        # 최대 로드 프로젝트 수


def count_pending_sessions() -> int:
    """frontmatter의 compiled 필드가 false인 세션 파일 수 카운트"""
    if not SESSIONS_DIR.exists():
        return 0
    try:
        count = 0
        fm_re = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
        field_re = re.compile(r"^compiled:\s*(\S+)", re.MULTILINE)
        for f in SESSIONS_DIR.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            m = fm_re.match(content)
            if not m:
                continue
            field_m = field_re.search(m.group(1))
            if field_m and field_m.group(1) == "false":
                count += 1
        return count
    except Exception:
        return 0


def parse_frontmatter(text: str) -> dict:
    """간단한 YAML frontmatter 파싱 (중첩 없는 key: value)"""
    fm_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    m = fm_re.match(text)
    if not m:
        return {}
    result = {}
    for line in m.group(1).splitlines():
        kv = line.split(":", 1)
        if len(kv) == 2:
            k = kv[0].strip()
            v = kv[1].strip().strip('"')
            result[k] = v
    return result


def load_active_projects() -> str:
    """
    L1 Pull: status:active 프로젝트를 updated 최신순으로 최대 L1_MAX_FILES개 로드.
    합산 L1_MAX_CHARS 초과 시 트리밍.
    반환: 컨텍스트 삽입용 문자열 (빈 문자열이면 주입 안 함)
    """
    if not PROJECTS_DIR.exists():
        return ""
    try:
        candidates = []
        for f in PROJECTS_DIR.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                fm = parse_frontmatter(content)
                if fm.get("status") == "active":
                    updated_str = fm.get("updated", "1970-01-01")
                    try:
                        updated_dt = datetime.strptime(updated_str, "%Y-%m-%d")
                    except ValueError:
                        updated_dt = datetime.min
                    candidates.append((updated_dt, f, content))
            except Exception:
                continue

        if not candidates:
            return ""

        # updated 내림차순 정렬
        candidates.sort(key=lambda x: x[0], reverse=True)
        top = candidates[:L1_MAX_FILES]

        parts = []
        total_chars = 0
        for _, f, content in top:
            if total_chars >= L1_MAX_CHARS:
                break
            remaining = L1_MAX_CHARS - total_chars
            chunk = content[:remaining]
            truncated = len(content) > remaining
            label = f"### L1 — [[projects/{f.stem}]]"
            if truncated:
                label += " _(토큰 상한으로 일부 생략)_"
            parts.append(f"{label}\n\n{chunk}")
            total_chars += len(chunk)

        if not parts:
            return ""

        header = "\n\n---\n## Active Projects (L1 자동 로드)\n\n"
        return header + "\n\n---\n".join(parts)

    except Exception:
        return ""


def documents_hard_stop_notice() -> str:
    """documents KPI hard-stop 감지 시 L0에 강력 경고 주입 (Gemini A안)"""
    if not DOCS_LINT_STATUS.exists():
        return ""
    try:
        status = json.loads(DOCS_LINT_STATUS.read_text(encoding="utf-8"))
        if not status.get("hard_stop"):
            return ""
        reason = status.get("hard_stop_reason", "unknown")
        deadline = status.get("schema_review_required_by", "미지정")
        return (
            "\n> 🔴 **DOCUMENTS HARD-STOP** — 스키마 리뷰 완료 전 신규 documents 생성 차단\n"
            f"> 사유: {reason}\n"
            f"> 리뷰 기한: {deadline}\n"
            f"> 해제 조건: wiki/decisions/documents-schema-review-YYYY-MM-DD.md 작성 + LINT 재실행\n"
            "> 사용자가 documents 신규 생성 요청 시 차단 상태 먼저 보고할 것.\n"
        )
    except Exception:
        return ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    # cwd guard: resolve()로 symlink/trailing-slash 처리
    try:
        cwd_path = Path(data.get("cwd", "")).resolve()
        brain_resolved = BRAIN_DIR.resolve()
        if brain_resolved != cwd_path and brain_resolved not in cwd_path.parents:
            sys.exit(0)
    except Exception:
        sys.exit(0)

    if not INDEX_FILE.exists():
        sys.exit(0)

    index_content = INDEX_FILE.read_text(encoding="utf-8")
    pending = count_pending_sessions()
    l1_context = load_active_projects()

    pending_notice = ""
    if pending >= 3:
        pending_notice = f"\n> ⚠️ 미컴파일 세션 {pending}개 — '오늘 세션 정리해줘'로 반영 권장\n"
    elif pending >= 1:
        pending_notice = f"\n> 미컴파일 세션 {pending}개 있음\n"

    docs_hardstop = documents_hard_stop_notice()

    context = f"""## My Brain — 세션 컨텍스트 (L0)

업무 지식 베이스 인덱스. 관련 요청 시 ~/Documents/my-brain/wiki/ 의 해당 페이지를 읽어 맥락 파악.
{pending_notice}{docs_hardstop}
{index_content}

---
주요 명령:
- 미팅 정리: '미팅 정리해줘' + 회의록 붙여넣기
- 세션 정리: '오늘 세션 정리해줘'
- 브리핑: '[이름/주제] 브리핑해줘'
- 현황: 'STEADY/월가세교역 현황 알려줘'
{l1_context}"""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
