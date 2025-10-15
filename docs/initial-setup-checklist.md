# 초기 세팅 체크리스트

**작성일**: 2025-10-15

---

## 📋 필수 설치 순서

### 1. ✅ Python 설치 (필수)

#### Windows 추천 방법
**Python 공식 사이트**:
1. https://www.python.org/downloads/ 접속
2. "Download Python 3.11.x" 버튼 클릭
3. 다운로드한 설치 파일 실행
4. **⚠️ 중요**: "Add Python to PATH" 체크박스 **반드시 체크**
5. "Install Now" 클릭

**설치 확인**:
```bash
python --version
# 출력: Python 3.11.x
```

---

### 2. ✅ `.env` 파일 생성 (완료)

`.env` 파일이 생성되었습니다.

**⚠️ 보안 경고**:
- 이 API 키는 절대 GitHub에 커밋하지 마세요!
- 가능하면 즉시 새 키로 교체하세요: https://platform.openai.com/api-keys

---

### 3. ⏳ 가상환경 생성 및 패키지 설치

Python 설치 후 실행:

```bash
# 프로젝트 폴더로 이동
cd C:\dev\portfolio\rag-portfolio

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows CMD)
venv\Scripts\activate

# 가상환경 활성화 (Windows PowerShell)
venv\Scripts\Activate.ps1

# 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt
```

**예상 설치 시간**: 3-5분

---

### 4. ⏳ 초기 데이터 확인

```bash
# data 폴더 확인
ls data/

# 필요한 파일:
# - data/index.faiss (있음)
# - data/text_chunks.txt (있음)
```

이미 있으므로 생략 가능.

---

### 5. ⏳ 서버 실행

```bash
# 가상환경이 활성화된 상태에서
python main.py

# 출력 예시:
# INFO:     Started server process [12345]
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 6. ⏳ 웹 브라우저에서 확인

```
http://localhost:8000
```

---

## 🔧 문제 해결

### Python 설치 후에도 `python` 명령어가 안 될 때

**원인**: PATH 환경변수에 등록되지 않음

**해결**:
1. Python 재설치 ("Add to PATH" 체크)
2. 또는 수동으로 PATH 추가:
   - 시스템 속성 → 환경 변수
   - Path 변수에 추가: `C:\Users\[사용자명]\AppData\Local\Programs\Python\Python311`

**임시 해결** (전체 경로로 실행):
```bash
C:\Users\[사용자명]\AppData\Local\Programs\Python\Python311\python.exe --version
```

---

### PowerShell에서 가상환경 활성화 안 될 때

**오류**:
```
venv\Scripts\Activate.ps1 : 이 시스템에서 스크립트를 실행할 수 없으므로...
```

**해결** (관리자 권한 PowerShell):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 패키지 설치 중 오류

**faiss-cpu 설치 실패 시**:
- Windows: Microsoft C++ Build Tools 필요
- https://visualstudio.microsoft.com/visual-cpp-build-tools/

**또는 Conda 사용**:
```bash
conda install -c conda-forge faiss-cpu
```

---

## 📝 다음 단계

1. ✅ Python 설치
2. ✅ `.env` 파일 생성
3. ⏳ 가상환경 생성 및 패키지 설치
4. ⏳ 서버 실행
5. ⏳ 웹에서 테스트

---

**Python 설치를 먼저 진행하세요!**
