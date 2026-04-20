#!/bin/bash
# my-brain update script
# 구조 파일(CLAUDE.md, session-start.py)만 업데이트. 개인 데이터 절대 미수정.

set -e

REPO="https://raw.githubusercontent.com/chulmin-dev/my-brain-template/main"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}my-brain updater${NC}"
echo "-----------------------------"

# 업데이트할 파일 목록 (개인 데이터 제외)
FILES=(
  "CLAUDE.md"
  ".hooks/session-start.py"
)

updated=0
skipped=0

for file in "${FILES[@]}"; do
  target="$SCRIPT_DIR/$file"
  dir="$(dirname "$target")"

  # 백업
  if [ -f "$target" ]; then
    backup="${target}.bak"
    cp "$target" "$backup"
  fi

  # 다운로드
  mkdir -p "$dir"
  if curl -fsSL "$REPO/$file" -o "$target" 2>/dev/null; then
    # 변경 여부 확인
    if [ -f "$backup" ] && diff -q "$backup" "$target" > /dev/null 2>&1; then
      mv "$backup" "$target"  # 동일하면 원본 복원
      echo -e "  ${YELLOW}skip${NC}  $file (변경 없음)"
      ((skipped++)) || true
    else
      rm -f "$backup"
      echo -e "  ${GREEN}✓${NC}     $file"
      ((updated++)) || true
    fi
  else
    # 다운로드 실패 시 백업 복원
    [ -f "$backup" ] && mv "$backup" "$target"
    echo -e "  ✗     $file (다운로드 실패 — 네트워크 확인)"
  fi
done

echo "-----------------------------"
echo -e "업데이트: ${GREEN}${updated}개${NC}  /  스킵: ${skipped}개"

if [ "$updated" -gt 0 ]; then
  echo ""
  echo -e "${CYAN}완료.${NC} Claude Code 재시작하면 적용돼."
else
  echo ""
  echo "이미 최신 버전이야."
fi
