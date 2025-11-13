#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
이전 세션 데이터를 현재 세션으로 마이그레이션하는 스크립트
"""
import sys
import os

# Windows 콘솔 UTF-8 인코딩 강제 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
from pathlib import Path

# 이전 세션 ID와 현재 세션 ID
OLD_SESSION_ID = "096b15ab-e92b-495b-aac4-ad9f11e61984"
NEW_SESSION_ID = "d006322a-03da-4fcf-9c8e-bee94a0a55bf"

# 이전 세션의 text_chunks.txt 읽기
old_session_path = Path(f"data/sessions/{OLD_SESSION_ID}/text_chunks.txt")

if not old_session_path.exists():
    print(f"❌ 이전 세션 파일을 찾을 수 없습니다: {old_session_path}")
    sys.exit(1)

# 텍스트 읽기 (청크 구분자 제거하고 전체 텍스트로)
with open(old_session_path, "r", encoding="utf-8") as f:
    content = f.read()

# 청크 구분선 제거
lines = content.split('\n')
clean_lines = []
for line in lines:
    # │로 시작하는 줄만 추출
    if line.startswith('│'):
        # 양쪽의 │ 제거
        clean_line = line.strip('│').strip()
        if clean_line:
            clean_lines.append(clean_line)

full_text = '\n'.join(clean_lines)

print(f"📖 이전 세션 텍스트 로드 완료: {len(full_text)} 글자")
print(f"📝 내용 미리보기:\n{full_text[:200]}...\n")

# FastAPI 서버에 추가
url = "http://localhost:8000/add-text"
data = {
    "title": "VectorMind 프로젝트 설명 (마이그레이션)",
    "content": full_text,
    "chunk_size": 512,
    "chunk_overlap": 100,
    "session_id": NEW_SESSION_ID
}

print(f"📤 현재 세션으로 데이터 전송 중...")
print(f"   Old Session: {OLD_SESSION_ID}")
print(f"   New Session: {NEW_SESSION_ID}")

try:
    response = requests.post(url, data=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n✅ 마이그레이션 완료!")
    print(f"   - 생성된 청크: {result['chunks_created']}개")
    print(f"   - 처리 시간: {result['processing_time']}초")
    print(f"   - 전체 청크 수: {result['total_chunks']}개")
    print(f"   - 인덱스 크기: {result['index_size']}MB")

except requests.exceptions.RequestException as e:
    print(f"❌ 마이그레이션 실패: {e}")
    if hasattr(e.response, 'text'):
        print(f"   응답: {e.response.text}")
    sys.exit(1)

print("\n🎉 이전 세션 데이터가 현재 세션으로 성공적으로 병합되었습니다!")
print("   브라우저를 새로고침하면 'VectorMind 프로젝트 설명' 파일이 목록에 표시됩니다.")
