# RAG Experiment Automation System v0.1

> **Retrieval-Augmented Generation (RAG) 시스템의 파라미터 최적화를 위한 자동화된 실험 프레임워크**

FastAPI 기반의 RAG 시스템에서 chunking, top-k, temperature 파라미터의 성능을 체계적으로 분석하고 최적화하는 도구입니다. 90개 실험을 통해 최적 파라미터 조합을 찾아내고, 비용-성능 트레이드오프를 분석합니다.

---

## 🚀 빠른 시작 (Quick Start)

### 로컬 실행
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 3. 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000

# 4. API 테스트
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"question": "인공지능이란 무엇인가요?", "top_k": 3, "temperature": 0.2}'
```

### Docker 실행
```bash
# Dockerfile 생성 후
docker build -t rag-experiment .
docker run -p 8000:8000 --env-file .env rag-experiment
```

### Google Colab
```python
# requirements.txt 설치 후
!pip install -r requirements.txt
!python -m experiments.grid_run
```

---

## 🔬 실험 자동화 흐름

### 1. Grid Search 실행
```bash
python -m experiments.grid_run
```
- **90개 파라미터 조합** 자동 테스트
- Chunk size: [256, 512]
- Top-k: [3, 5, 8]  
- Temperature: [0.2, 0.5, 0.8]

### 2. 결과 분석
```bash
python -m experiments.analyze_results
```
- 성능 지표 계산 (Recall@5, F1 Score)
- 비용 및 응답 시간 분석
- 시각화 생성 (`performance_analysis.png`)

### 3. 튜닝 리포트 생성
- `tuning_report_v1.md` 자동 생성
- 최적 파라미터 조합 추천
- 실무 적용 가이드라인

---

## 📊 최근 실험 결과

### 최적 파라미터 조합
- **Chunk Size**: 256
- **Top-k**: 3  
- **Temperature**: 0.2
- **성능**: Recall@5 = 1.000, F1 = 1.000
- **비용**: $0.0284 per query

### 전체 실험 요약
- **총 실험 수**: 90개
- **완벽 점수**: 42개 실험
- **평균 응답 시간**: 1274.8ms
- **평균 비용**: $0.0541

---

## 📁 프로젝트 구조

```
gpt-fastapi-app/
├── main.py                    # FastAPI RAG 서버
├── config.py                  # 설정 관리
├── prompt_template.py         # 프롬프트 템플릿
├── experiments/
│   ├── grid_run.py           # 그리드 서치 실행
│   ├── analyze_results.py    # 결과 분석
│   ├── generate_embedding.py # 임베딩 생성
│   └── results/
│       ├── tuning_report_v1.md
│       └── performance_analysis.png
├── utils/
│   ├── data_loader.py        # 데이터 로더
│   └── prompt_engine.py      # 프롬프트 엔진
├── data/
│   ├── index.faiss          # 벡터 인덱스
│   └── text_chunks.txt      # 텍스트 청크
└── logs/                    # 실험 로그
```

---

## 🔗 링크

- **GitHub**: [https://github.com/Jaeyeon-Kang/gpt-fastapi-app](https://github.com/Jaeyeon-Kang/gpt-fastapi-app)
- **API 문서**: `http://localhost:8000/docs` (서버 실행 후)
- **실험 문서**: [experiments/document.md](experiments/document.md)
- **튜닝 리포트**: [experiments/results/tuning_report_v1.md](experiments/results/tuning_report_v1.md)

### 📹 3분 소개 영상
> **추후 추가 예정** - 실험 과정 및 결과 시연 영상

---

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: OpenAI GPT-4, text-embedding-3-small
- **Vector Search**: Faiss
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **Text Processing**: LangChain, tiktoken

---

## 📈 성능 지표

| 지표 | 값 | 설명 |
|------|-----|------|
| Recall@5 | 1.000 | 상위 5개 문서 중 관련 문서 포함율 |
| F1 Score | 1.000 | 정밀도와 재현율의 조화평균 |
| Latency | 1092ms | 평균 응답 시간 |
| Cost | $0.0284 | 쿼리당 평균 비용 |

---

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 📞 문의

- **이슈**: [GitHub Issues](https://github.com/Jaeyeon-Kang/gpt-fastapi-app/issues)
- **블로그**: 추후 추가 예정
- **이메일**: 추후 추가 예정
