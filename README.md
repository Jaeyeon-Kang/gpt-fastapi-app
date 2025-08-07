# VectorMind v0.1

> **벡터 + 마인드의 조합**

VectorMind는 문서를 이해하고 질문에 답변하는 AI 시스템입니다. 문서를 벡터로 변환하여 저장하고, 질문과 가장 관련성 높은 내용을 찾아서 GPT가 답변을 생성합니다. 

## 🎯 이 프로젝트는 무엇인가요?

- **문서 업로드**: PDF, Word, 텍스트 파일을 업로드하면 자동으로 분석합니다
- **질문-답변**: 업로드한 문서에 대해 자연어로 질문하면 AI가 답변합니다
- **실시간 테스트**: 다양한 설정으로 답변 품질을 실시간으로 조정할 수 있습니다
- **성능 최적화**: 자동으로 최적의 설정을 찾아주는 실험 기능이 있습니다

## 🚀 어떻게 사용하나요?

### 1단계: 문서 준비
- PDF, Word(.docx), 텍스트(.txt), CSV 파일을 준비하세요
- 또는 직접 텍스트를 입력할 수도 있습니다

### 2단계: 문서 업로드
- "파일 업로드" 탭에서 파일을 선택하거나
- "텍스트 입력" 탭에서 직접 내용을 입력하세요

### 3단계: 질문하기
- "RAG 테스트" 탭에서 문서에 대한 질문을 입력하세요
- 예시: "이 문서의 주요 내용은 무엇인가요?", "특정 개념에 대해 설명해주세요"

### 4단계: 설정 조정 (선택사항)
- **Top-k**: 참고할 문서 조각의 개수 (3-10개 권장)
- **Temperature**: 답변의 창의성 (0.2=정확함, 0.8=창의적)
- **System Prompt**: AI의 역할 설정

### 5단계: 결과 확인
- AI가 문서를 참고하여 답변을 생성합니다
- 답변 아래에 참고한 문서 내용도 함께 표시됩니다

## 🔬 실험 기능 (고급 사용자)

"실험 결과" 탭에서는 다양한 설정 조합을 자동으로 테스트한 결과를 확인할 수 있습니다:
- 어떤 설정이 가장 좋은 답변을 만드는지
- 문서 분할 크기, 검색 개수, AI 창의성의 영향
- 성능 점수와 최적 설정 추천

---

## 🧠 VectorMind 프로젝트 특징

| 항목 | 특징 |
|------|------|
| **벡터 저장소** | FAISS (Facebook AI Similarity Search) - 고성능 벡터 유사도 검색 |
| **임베딩 모델** | OpenAI text-embedding-3-small API - 1536차원 벡터 생성 |
| **데이터 처리** | 텍스트 파일 기반 (text_chunks.txt) - 실험 최적화된 구조 |
| **검색 방식** | FAISS L2 거리 기반 top-k 검색 - 빠른 유사도 계산 |
| **AI 응답** | GPT-4-1106-preview - 고품질 문맥 기반 답변 생성 |
| **파라미터 최적화** | Grid Search 자동화 - chunk_size, top_k, temperature 조합 테스트 |
| **웹 인터페이스** | FastAPI + HTML/CSS/JS - 실시간 질문-답변 및 실험 결과 시각화 |
| **파일 지원** | PDF, DOCX, TXT, CSV 업로드 - 다양한 문서 형식 처리 |
| **실험 자동화** | 배치 처리 + CSV 결과 저장 - 체계적인 성능 분석 |
| **로깅 시스템** | 대화 기록 자동 저장 - 사용자 상호작용 추적 |
| **배포 환경** | Render 클라우드 플랫폼 - 실제 서비스 운영 |

---

## 🌐 웹 인터페이스 접속

### 실시간 데모
🔗 **바로 사용해보기**: [https://gpt-fastapi-app.onrender.com/](https://gpt-fastapi-app.onrender.com/)

### 주요 기능
- **📝 문서 업로드**: PDF, Word, 텍스트 파일 지원
- **🤖 AI 질문-답변**: 문서 내용 기반 자연어 대화
- **⚙️ 실시간 설정 조정**: 답변 품질을 즉시 조정
- **📊 실험 결과 확인**: 최적 설정 자동 분석

### 📸 실제 작동 예시

![RAG System Demo - 답변 결과](images/스크린샷1.png)
*실시간 테스트 화면 예시*

![RAG System Demo - 실험 결과](images/스크린샷2.png)
*동적으로 로딩되는 실험 결과 화면 예시*

> 🔗 **실시간 데모**: [https://gpt-fastapi-app.onrender.com/](https://gpt-fastapi-app.onrender.com/)

### 환경 설정

1. **환경 변수 설정**
   ```bash
   # .env 파일 생성
   cp .env.example .env
   
   # .env 파일을 편집하여 실제 API 키 입력
   # OPENAI_API_KEY=sk-your_actual_api_key_here
   ```

   ⚠️ **보안 주의사항**: `.env` 파일은 절대 Git에 커밋하지 마세요!

2. **OpenAI API 키 발급**
   - [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키 발급
   - `.env` 파일에 `OPENAI_API_KEY=sk-...` 형태로 입력

### 로컬 실행
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 서버 실행
python main.py

# 3. 웹 인터페이스 접속
# 브라우저에서 http://localhost:8000 주소로 접속
```

### 💡 사용 팁
- **📝 텍스트 직접 입력**: 파일 없이도 바로 텍스트를 입력해서 테스트할 수 있습니다
- **🔍 구체적인 질문**: "이 문서의 핵심은?"보다는 "이 문서에서 AI의 정의는 무엇인가요?"처럼 구체적으로 질문하세요
- **⚙️ 설정 실험**: Top-k와 Temperature를 조정해서 답변 품질을 비교해보세요
- **📊 결과 분석**: 실험 결과 탭에서 어떤 설정이 가장 좋은지 확인하세요

---

## 🔬 실험 기능 (개발자용)

### 자동 최적화 실험
시스템이 자동으로 다양한 설정을 테스트하여 최적의 조합을 찾아줍니다:

```bash
# 실험 실행 (선택사항)
python -m experiments.grid_run
```

**실험 내용**:
- 문서 분할 크기 (256, 512자)
- 검색할 문서 조각 수 (3, 5, 8개)
- AI 창의성 수준 (0.2, 0.5, 0.8)

**결과 확인**: 웹 인터페이스의 "실험 결과" 탭에서 자동으로 로딩됩니다.

---

## 📁 프로젝트 구조

```
gpt-fastapi-app/
├── main.py                    # FastAPI RAG 서버 (API 로직)
├── config.py                  # 프로젝트 설정 관리
├── requirements.txt           # 파이썬 의존성 목록
├── .env.example               # 환경 변수 예시 파일
├── prompt_template.py         # 프롬프트 템플릿
├── static/
│   └── index.html             # 프론트엔드 UI
├── experiments/
│   ├── grid_run.py            # 그리드 서치 실행 스크립트
│   ├── analyze_results.py     # (참고용) 결과 분석 스크립트
│   └── results/               # 실험 결과 CSV 저장 폴더
│       └── *.csv
├── utils/
│   └── data_loader.py         # 데이터 로더 유틸
├── data/
│   ├── index.faiss            # Faiss 벡터 인덱스
│   └── text_chunks.txt        # 원본 텍스트 데이터
└── logs/                      # 대화 로그 저장 폴더
```

---

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: OpenAI GPT-4, text-embedding-3-small
- **Vector Search**: Faiss (Facebook AI Similarity Search)
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML, CSS, JavaScript (Vanilla)

---

## 🤝 기여하기

언제나 환영합니다. 이슈를 등록하거나 Pull Request를 보내주세요.

1.  Repository를 Fork합니다.
2.  새로운 기능 브랜치를 생성합니다. (`git checkout -b feature/amazing-feature`)
3.  변경 사항을 커밋합니다. (`git commit -m 'Add amazing feature'`)
4.  브랜치에 푸시합니다. (`git push origin feature/amazing-feature`)
5.  Pull Request를 생성합니다.

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.
