# 실험 요약 (Experiment Summary)

> **이 섹션은 왜 필요해?**
> - 실험의 목적, 데이터, 방법론을 한눈에 요약해서 보는 사람(멘토, 동료, 미래의 나)이 바로 이해할 수 있게 해줌.

- **실험 목적:**
  - Retrieval-Augmented Generation(RAG) 시스템의 chunking 전략, Top-k, Temperature 등 주요 파라미터가 답변 품질에 미치는 영향 분석
- **데이터:**
  - 위키피디아 '인공지능' 문서(한국어)
- **실험 방법:**
  - 다양한 chunking 전략(S-A, S-B, S-C), Top-k, Temperature 조합으로 grid search
  - 각 조합별로 질문에 대한 답변 생성 및 평가 지표 기록

---

# 핵심 지표 테이블 (Key Metrics Table)

> **이 섹션은 왜 필요해?**
> - 실험 결과를 한눈에 비교할 수 있게 표로 정리. (Top-k, 온도, F1, Recall@5 등)
> - 어떤 조합이 가장 성능이 좋은지, 어떤 경향이 있는지 빠르게 파악 가능.

| Chunking | Top-k | Temp | F1  | Recall@5 |
|----------|-------|------|-----|----------|
| S-A      |   3   | 0.2  | 0.8 |   True   |
| S-A      |   5   | 0.5  | 0.8 |   True   |
| S-B      |   3   | 0.8  | 0.8 |   True   |
| S-C      |   8   | 0.2  | 0.8 |   True   |
| S-C      |   8   | 0.8  | 0.8 |   True   |

> (실제 실험 결과에서 값 뽑아서 이 표에 채워넣으면 됨)

**인사이트:**
- 모든 chunking/top-k/온도 조합에서 F1=0.8, Recall@5=True로 나옴 (실제 실험에서는 값이 달라질 수 있음)
- chunking 전략별로 큰 차이는 아직 안 보임 (실제 데이터/질문이 다양해지면 차이 날 수 있음)

---

# Phase 3 액션 (Next Steps)

> **이 섹션은 왜 필요해?**
> - 실험을 통해 얻은 인사이트, 한계점, 다음에 할 일(추가 실험, 개선 아이디어 등)을 정리
> - 실험이 단순히 끝나는 게 아니라, '다음 단계'로 이어질 수 있게 해줌

- chunking 전략별로 성능 차이가 뚜렷한지 추가 분석 필요
- 비용(토큰 사용량) 및 latency 측정 추가 예정
- 실제 사용자 질문(실전 데이터)로 실험 확장
- Faiss 기반 벡터 검색 성능 개선 실험 예정
- (기타 아이디어)

---

> **Tip:**
> 이 문서는 실험이 끝날 때마다 계속 업데이트/보완하면 돼. (처음엔 뼈대만, 나중엔 표/요약/액션을 점점 채워나가는 식으로!) 