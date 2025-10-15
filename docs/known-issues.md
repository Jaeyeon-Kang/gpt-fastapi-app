# VectorMind - Known Issues & Fixes

**작성일**: 2025-10-15
**목적**: 프로젝트 실행 시 발생 가능한 오류 및 해결 방법 정리

---

## 🔍 잠재적 문제점 분석

### 1. ⚠️ 환경 변수 설정 누락
**증상**: `openai.AuthenticationError` 또는 `API key not found`

**원인**: `.env` 파일이 없거나 `OPENAI_API_KEY`가 설정되지 않음

**해결 방법**:
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일을 열어 API 키 입력
# OPENAI_API_KEY=sk-your_actual_api_key_here
```

---

### 2. ⚠️ 의존성 패키지 누락
**증상**: `ModuleNotFoundError: No module named 'xxx'`

**원인**: requirements.txt의 패키지가 설치되지 않음

**해결 방법**:
```bash
# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

**주의사항**:
- `requirements.txt`에 버전이 명시되지 않은 패키지들 존재:
  - `numpy`, `faiss-cpu`, `pytest`, `tiktoken`, `langchain`, `pandas` 등
  - 호환성 문제 발생 가능

**권장 수정** (requirements.txt):
```
numpy>=1.24.0,<2.0.0
faiss-cpu>=1.7.4
pytest>=7.4.0
tiktoken>=0.5.0
langchain>=0.1.0
pandas>=2.0.0
python-multipart>=0.0.6
PyPDF2>=3.0.0
python-docx>=0.8.11
boto3>=1.28.0
```

---

### 3. ⚠️ FAISS 인덱스 파일 누락
**증상**: `FileNotFoundError: data/index.faiss not found`

**원인**:
- 초기 실행 시 인덱스 파일이 없음
- `data/text_chunks.txt`가 없거나 비어있음

**해결 방법**:
```python
# main.py의 ensure_faiss_index() 함수가 자동으로 생성하지만
# 수동으로 생성하려면:

cd experiments
python generate_embedding.py
```

**또는 웹 인터페이스에서 문서 업로드**

---

### 4. ⚠️ LangChain 동적 import 문제
**파일**: `main.py:111`

**코드**:
```python
def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # 🔴 함수 내부 import
    ...
```

**문제점**:
- 함수가 호출될 때마다 import 실행 (비효율)
- LangChain 버전 변경 시 import 경로 변경 가능
- `langchain-text-splitters` 패키지로 분리됨 (최신 버전)

**해결 방법**:
```python
# main.py 상단에 추가
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list:
    """텍스트를 청크로 나눕니다."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return text_splitter.split_text(text)
```

---

### 5. ⚠️ S3 예외 처리 문제
**파일**: `utils/s3_store.py:41`

**코드**:
```python
except self.s3.exceptions.NoSuchKey:  # type: ignore
```

**문제점**:
- boto3 클라이언트의 예외는 런타임에 동적 생성됨
- 타입 체커가 인식하지 못함
- `type: ignore` 주석으로 우회

**더 안전한 방법**:
```python
from botocore.exceptions import ClientError

def append_text(self, session_id: str, name: str, text: str):
    key = self._key(session_id, name)
    try:
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        prev = obj["Body"].read()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            prev = b""
        else:
            raise
    self.s3.put_object(Bucket=self.bucket, Key=key, Body=prev + text.encode("utf-8"))
```

---

### 6. ⚠️ FAISS 인덱스 초과 접근
**파일**: `main.py:337`

**코드**:
```python
valid_pairs = [(rank, idx, float(D[0][rank])) for rank, idx in enumerate(I[0]) if 0 <= idx < len(chunks)]
```

**문제점**:
- FAISS가 반환한 인덱스가 `chunks` 리스트 범위를 초과할 수 있음
- 인덱스 업데이트와 텍스트 파일이 불일치할 경우 발생

**현재는 방어 코드가 있지만, 더 명확한 로깅 필요**:
```python
valid_pairs = []
for rank, idx in enumerate(I[0]):
    if 0 <= idx < len(chunks):
        valid_pairs.append((rank, idx, float(D[0][rank])))
    else:
        print(f"⚠️  경고: FAISS 인덱스 {idx}가 chunks 범위({len(chunks)})를 초과했습니다.")
```

---

### 7. ⚠️ 세션 경로 생성 타이밍
**파일**: `main.py:184-187`

**코드**:
```python
def get_paths_for_session(session_id: Optional[str]) -> Tuple[str, str]:
    if not session_id:
        return config.INDEX_PATH, config.TEXT_PATH
    base = Path("data/sessions") / session_id
    index_path = str(base / "index.faiss")
    text_path = str(base / "text_chunks.txt")
    return index_path, text_path
```

**문제점**:
- 디렉토리가 존재하지 않아도 경로만 반환
- 나중에 파일 접근 시 `FileNotFoundError` 발생 가능

**개선 방법**:
```python
def get_paths_for_session(session_id: Optional[str], ensure_dir: bool = False) -> Tuple[str, str]:
    if not session_id:
        return config.INDEX_PATH, config.TEXT_PATH
    base = Path("data/sessions") / session_id
    if ensure_dir:
        base.mkdir(parents=True, exist_ok=True)
    index_path = str(base / "index.faiss")
    text_path = str(base / "text_chunks.txt")
    return index_path, text_path
```

---

### 8. ⚠️ Rate Limiting 메모리 누수 가능성
**파일**: `utils/rate_limit.py:8-9`

**코드**:
```python
_daily_counts: Dict[Tuple[str, str], Tuple[int, float]] = {}
_burst_counts: Dict[Tuple[str, str], Tuple[int, float]] = {}
```

**문제점**:
- 전역 딕셔너리가 계속 증가 (만료된 세션도 유지)
- 장기 실행 시 메모리 누수

**개선 방법**:
```python
def _cleanup_expired():
    """만료된 항목 제거"""
    now = _now()
    global _daily_counts, _burst_counts

    # 일일 윈도우 만료 항목 제거
    expired_daily = [k for k, (_, start) in _daily_counts.items()
                     if now - start >= config.RATE_WINDOW_SECONDS * 2]
    for k in expired_daily:
        del _daily_counts[k]

    # 버스트 윈도우 만료 항목 제거
    expired_burst = [k for k, (_, start) in _burst_counts.items()
                     if now - start >= config.BURST_WINDOW_SECONDS * 2]
    for k in expired_burst:
        del _burst_counts[k]

def check_limits(req: Request, name: str, daily_limit: int, burst_limit: int, session_id: Optional[str] = None):
    # 100번 호출마다 정리
    if len(_daily_counts) > 100:
        _cleanup_expired()
    # ... 기존 로직
```

---

### 9. ⚠️ CSV 파일 처리 취약점
**파일**: `main.py:98-101`

**코드**:
```python
elif file.filename.endswith('.csv'):
    csv_text = content.decode('utf-8')
    return csv_text
```

**문제점**:
- CSV 구조 정보 손실 (단순 텍스트 변환)
- 구분자, 인용 문자 무시
- 대용량 CSV 메모리 오버플로

**개선 방법**:
```python
elif file.filename.endswith('.csv'):
    import pandas as pd
    df = pd.read_csv(io.BytesIO(content))
    # 구조화된 텍스트로 변환
    text = f"CSV 파일: {file.filename}\n\n"
    text += f"컬럼: {', '.join(df.columns)}\n\n"
    text += df.to_string(index=False)
    return text
```

---

### 10. ⚠️ 에러 메시지 보안
**파일**: 여러 곳

**예시**:
```python
raise HTTPException(status_code=500, detail=f"임베딩 생성 오류: {e}")
```

**문제점**:
- 상세한 에러 메시지가 클라이언트에 노출
- 내부 구조 정보 유출 가능 (보안 위험)

**개선 방법**:
```python
import logging
logger = logging.getLogger(__name__)

try:
    # ...
except Exception as e:
    logger.error(f"임베딩 생성 오류: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="임베딩 생성 중 오류가 발생했습니다.")
```

---

## 🚀 빠른 문제 해결 체크리스트

### 실행 전 체크리스트
- [ ] `.env` 파일이 존재하고 `OPENAI_API_KEY`가 설정되어 있는가?
- [ ] `pip install -r requirements.txt`를 실행했는가?
- [ ] `data/` 폴더가 존재하는가?
- [ ] Python 버전이 3.8 이상인가? (`python --version`)

### 실행 시 오류 체크
- [ ] `ModuleNotFoundError` → 패키지 재설치
- [ ] `FileNotFoundError` → 문서 업로드 먼저 진행
- [ ] `AuthenticationError` → API 키 확인
- [ ] `HTTPException 429` → Rate Limit 초과, 잠시 대기

---

## 🛠️ 권장 개선 작업

### 즉시 수정 권장 (Priority High)
1. ✅ requirements.txt에 버전 명시
2. ✅ LangChain import를 상단으로 이동
3. ✅ S3 예외 처리 개선 (ClientError 사용)
4. ✅ 에러 메시지 보안 처리

### 단기 개선 (Priority Medium)
5. ✅ Rate Limiting 메모리 정리 함수 추가
6. ✅ CSV 처리 로직 개선
7. ✅ FAISS 인덱스 불일치 로깅 추가
8. ✅ 세션 디렉토리 자동 생성

### 장기 개선 (Priority Low)
9. ✅ 로깅 시스템 구축 (logging 모듈)
10. ✅ 유닛 테스트 작성 (pytest)
11. ✅ 타입 힌트 보완 (mypy 검사)
12. ✅ 문서화 개선 (docstring)

---

## 📋 테스트 방법

### 로컬 테스트
```bash
# 1. 서버 실행
python main.py

# 2. 브라우저에서 확인
# http://localhost:8000

# 3. 문서 업로드 테스트
# - "문서 업로드" 탭에서 PDF/DOCX 파일 업로드
# - "RAG 테스트" 탭에서 질문 입력

# 4. API 직접 테스트 (curl)
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"question": "이 문서의 주요 내용은?", "top_k": 3, "temperature": 0.7}'
```

### 오류 로그 확인
```bash
# 대화 로그
cat logs/chat_logs.csv

# 검색 로그
cat logs/search_logs.csv

# 서버 콘솔 출력 확인
# Ctrl+C로 서버 종료 전 에러 메시지 확인
```

---

## 🔧 긴급 수정 스크립트

### 1. 의존성 버전 고정
```bash
# 현재 설치된 버전 저장
pip freeze > requirements-lock.txt
```

### 2. 데이터 폴더 초기화
```bash
# 인덱스 재생성
rm -f data/index.faiss
python experiments/generate_embedding.py
```

### 3. Rate Limit 카운터 초기화
```python
# Python REPL에서 실행
import requests
requests.post("http://localhost:8000/admin/reset-limits")  # (엔드포인트 구현 필요)
```

---

**Last Updated**: 2025-10-15
**Next Review**: 문제 발생 시 즉시 업데이트
