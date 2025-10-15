# VectorMind 설치 가이드

**작성일**: 2025-10-15
**대상**: 처음 프로젝트를 설치하는 개발자

---

## 📋 사전 요구사항

### 1. Python 설치

#### Windows
```bash
# 방법 1: Python 공식 사이트에서 다운로드
# https://www.python.org/downloads/
# - Python 3.8 이상 버전 다운로드
# - 설치 시 "Add Python to PATH" 체크박스 반드시 선택!

# 방법 2: Chocolatey 사용 (관리자 권한 PowerShell)
choco install python

# 방법 3: winget 사용 (Windows 10/11)
winget install Python.Python.3.11
```

#### macOS
```bash
# 방법 1: Homebrew 사용 (권장)
brew install python@3.11

# 방법 2: Python 공식 사이트
# https://www.python.org/downloads/
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# CentOS/RHEL
sudo yum install python311 python311-pip

# Arch Linux
sudo pacman -S python
```

#### 설치 확인
```bash
python --version
# 또는
python3 --version

# 출력 예시: Python 3.11.x
```

---

## 🚀 빠른 시작 (Quick Start)

### 1단계: 프로젝트 클론 또는 다운로드
```bash
# Git 클론
git clone https://github.com/your-username/rag-portfolio.git
cd rag-portfolio

# 또는 ZIP 다운로드 후 압축 해제
```

### 2단계: 가상환경 생성 (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# 활성화되면 프롬프트에 (venv) 표시됨
```

### 3단계: 의존성 패키지 설치
```bash
pip install -r requirements.txt

# 설치 중 오류 발생 시:
pip install --upgrade pip
pip install -r requirements.txt
```

### 4단계: 환경 변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env

# .env 파일 편집
# OPENAI_API_KEY=sk-your_actual_api_key_here
```

**OpenAI API 키 발급 방법**:
1. https://platform.openai.com/ 접속
2. 로그인 또는 회원가입
3. API Keys 메뉴 선택
4. "Create new secret key" 클릭
5. 생성된 키를 `.env` 파일에 붙여넣기

### 5단계: 서버 실행
```bash
python main.py

# 출력 예시:
# INFO:     Started server process [12345]
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6단계: 웹 브라우저에서 접속
```
http://localhost:8000
```

---

## 📦 의존성 패키지 상세

### 현재 requirements.txt
```txt
annotated-types==0.7.0
anyio==4.9.0
certifi==2025.4.26
click==8.1.8
distro==1.9.0
fastapi==0.115.12
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.10
jiter==0.9.0
openai==1.77.0
pydantic==2.11.4
pydantic_core==2.33.2
python-dotenv==1.1.0
sniffio==1.3.1
starlette==0.46.2
tqdm==4.67.1
typing-inspection==0.4.0
typing_extensions==4.13.2
uvicorn==0.34.2
numpy
faiss-cpu
pytest
tiktoken
langchain
pandas
python-multipart
PyPDF2
python-docx
boto3
```

### 버전 미명시 패키지 (호환성 주의)
다음 패키지들은 버전이 명시되지 않아 최신 버전이 설치됩니다:
- `numpy`, `faiss-cpu`, `pytest`, `tiktoken`, `langchain`, `pandas`, `python-multipart`, `PyPDF2`, `python-docx`, `boto3`

**권장 버전 고정 (requirements-lock.txt)**:
```txt
numpy>=1.24.0,<2.0.0
faiss-cpu>=1.7.4,<2.0.0
pytest>=7.4.0,<8.0.0
tiktoken>=0.5.0,<1.0.0
langchain>=0.1.0,<0.2.0
pandas>=2.0.0,<3.0.0
python-multipart>=0.0.6,<1.0.0
PyPDF2>=3.0.0,<4.0.0
python-docx>=0.8.11,<1.0.0
boto3>=1.28.0,<2.0.0
```

---

## 🔧 문제 해결 (Troubleshooting)

### 문제 1: Python 명령어를 찾을 수 없음
```bash
# 증상
'python' is not recognized as an internal or external command

# 해결
# 1. Python이 설치되지 않음 → 위 "Python 설치" 섹션 참조
# 2. PATH 환경변수에 등록되지 않음 → Python 재설치 (Add to PATH 체크)
# 3. python3 명령어 사용:
python3 --version
python3 main.py
```

### 문제 2: pip 명령어를 찾을 수 없음
```bash
# Python 3.4+ 에는 pip가 기본 포함
python -m pip --version

# pip 업그레이드
python -m pip install --upgrade pip
```

### 문제 3: 가상환경 활성화 안 됨 (Windows PowerShell)
```powershell
# 증상
venv\Scripts\activate : 이 시스템에서 스크립트를 실행할 수 없으므로...

# 해결: PowerShell 실행 정책 변경 (관리자 권한)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 다시 시도
venv\Scripts\activate
```

### 문제 4: faiss-cpu 설치 실패
```bash
# Windows에서 Microsoft C++ Build Tools 필요할 수 있음
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 또는 conda 사용 (Anaconda/Miniconda 설치 후)
conda install -c conda-forge faiss-cpu
```

### 문제 5: langchain 버전 충돌
```bash
# 최신 langchain은 패키지가 분리됨
pip install langchain langchain-text-splitters

# 또는 구버전 사용
pip install langchain==0.1.0
```

### 문제 6: OpenAI API 인증 오류
```bash
# 증상
openai.AuthenticationError: Incorrect API key provided

# 해결
# 1. .env 파일에 API 키가 올바르게 입력되었는지 확인
# 2. API 키 앞뒤 공백 제거
# 3. 따옴표 없이 입력 (OPENAI_API_KEY=sk-xxx...)
# 4. OpenAI 플랫폼에서 API 키 활성 상태 확인
```

### 문제 7: 포트 8000이 이미 사용 중
```bash
# 증상
ERROR: [Errno 48] Address already in use

# 해결 1: 다른 포트 사용
uvicorn main:app --port 8001

# 해결 2: 기존 프로세스 종료 (Windows)
netstat -ano | findstr :8000
taskkill /PID [프로세스ID] /F

# 해결 2: 기존 프로세스 종료 (macOS/Linux)
lsof -ti:8000 | xargs kill -9
```

---

## 🧪 설치 확인

### 테스트 스크립트 실행
```bash
# Python REPL에서 테스트
python
>>> import fastapi
>>> import openai
>>> import faiss
>>> import pandas
>>> print("모든 패키지가 정상적으로 설치되었습니다!")
>>> exit()
```

### pytest 실행 (선택)
```bash
# 테스트 파일이 있다면
pytest

# 테스트 파일이 없으면 생성 필요 (TODO)
```

### 서버 상태 확인
```bash
# 서버 실행 후 다른 터미널에서
curl http://localhost:8000
# 또는
curl http://localhost:8000/health  # (엔드포인트 구현 필요)
```

---

## 📁 프로젝트 구조 확인

설치 후 다음 구조가 있는지 확인:
```
rag-portfolio/
├── .env                   # ✅ 생성됨 (API 키 포함)
├── .env.example           # 예시 파일
├── venv/                  # ✅ 가상환경 (설치된 패키지들)
├── data/
│   ├── index.faiss        # 초기에는 없을 수 있음 (자동 생성)
│   └── text_chunks.txt    # 문서 청크
├── logs/                  # 로그 파일 (자동 생성)
├── main.py                # FastAPI 서버
├── config.py              # 설정
├── requirements.txt       # 의존성 목록
└── static/
    └── index.html         # 프론트엔드
```

---

## 🎯 다음 단계

### 1. 문서 업로드 테스트
1. 웹 브라우저에서 http://localhost:8000 접속
2. "문서 업로드" 탭 선택
3. PDF, DOCX, TXT 파일 업로드
4. "RAG 테스트" 탭에서 질문 입력

### 2. API 직접 테스트
```bash
# 질의 응답 API 테스트
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "question": "이 문서의 주요 내용은?",
    "top_k": 3,
    "temperature": 0.7
  }'
```

### 3. 실험 결과 확인
```bash
# Grid Search 실험 실행 (선택)
cd experiments
python grid_run.py

# 웹에서 실험 결과 확인
# http://localhost:8000 → "실험 결과" 탭
```

---

## 🔒 보안 주의사항

### ⚠️ 절대 커밋하지 말 것
- `.env` 파일 (API 키 포함)
- `venv/` 폴더 (가상환경)
- `__pycache__/` 폴더
- `*.pyc` 파일

### .gitignore 확인
```gitignore
.env
venv/
__pycache__/
*.pyc
.DS_Store
logs/*.csv
data/sessions/
```

---

## 💡 개발 환경 권장 사항

### IDE/에디터
- **VS Code** (권장)
  - Python 확장 설치
  - Pylance (타입 체크)
  - Black Formatter (코드 포맷팅)
- **PyCharm**
- **Cursor** (AI 코드 어시스턴트)

### VS Code 설정 (.vscode/settings.json)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### 유용한 개발 도구
```bash
# 코드 포맷팅
pip install black
black .

# 린팅
pip install pylint
pylint main.py

# 타입 체크
pip install mypy
mypy main.py

# 자동 import 정리
pip install isort
isort .
```

---

## 📚 추가 학습 자료

- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/
- **OpenAI API 가이드**: https://platform.openai.com/docs
- **FAISS 튜토리얼**: https://github.com/facebookresearch/faiss/wiki
- **LangChain 문서**: https://python.langchain.com/docs/

---

## 🆘 도움이 필요한가요?

- GitHub Issues: (저장소 URL)/issues
- 이메일: your-email@example.com
- 디스코드: (초대 링크)

---

**Last Updated**: 2025-10-15
**Tested On**: Windows 11, macOS Sonoma, Ubuntu 22.04
