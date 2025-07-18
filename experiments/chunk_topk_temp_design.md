# RAG 시스템 성능 최적화 실험 (Chunking & Param Tuning)

- **실험 ID**: `exp-001`
- **버전**: `v1.0`
- **작성자**: Bella
- **리뷰어**: Monday (AI Assistant)

---

## 1. Chunking 전략 비교 매트릭스

RAG 시스템의 검색(Retrieval) 성능은 텍스트를 어떤 단위로 잘라 저장(Chunking)하느냐에 크게 의존합니다. 아래는 여러 Chunking 전략을 비교하고 최적의 방안을 찾기 위한 계획입니다.

| 전략 ID | 전략 이름 | 설명 | 추가 패키지 | 예상 토큰/임베딩 비용 | 평가 지표 (정의) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S-A** | **문단 기준 분할 (Baseline)** | 소스 텍스트의 문단(`\\n\\n`)을 기준으로 분할합니다. | - | 낮음 (기본) | **Recall@5**: 상위 5개 검색 결과에 정답 Chunk가 포함되었는지 여부. |
| **S-B** | **고정 토큰 크기 분할** | 모든 Chunk를 **150 토큰** 기준으로 자릅니다. (Overlap: 20 토큰) | - | 중간 (토큰 수 증가) | **Hit@1**: 상위 1개 검색 결과가 바로 정답 Chunk인지 여부. |
| **S-C** | **재귀적 문자 분할** | 의미가 깨지지 않는 선에서 재귀적으로 분할합니다. (by LangChain) | `langchain-text-splitters` | 높음 (라이브러리 오버헤드) | **F1 Score**: Recall과 Precision의 조화 평균으로, 검색 성능을 종합적으로 측정. |

---

## 2. Top-k 및 Temperature 실험 계획

검색된 Chunk의 개수(Top-k)와 LLM의 창의성(Temperature)은 답변의 품질을 결정하는 중요한 파라미터입니다. 아래는 다양한 질문 유형에 따라 최적의 조합을 찾기 위한 Grid Search 계획입니다.

**질문 셋업**:
- **사실 기반 질문 (5개 샘플)**: "이순신 장군의 생년월일은?", "거북선의 주요 특징은?" ...
- **요약 질문 (5개 샘플)**: "명량해전에 대해 3문장으로 요약해줘.", "난중일기의 핵심 내용을 요약해줘." ...
- **창의적/추론 질문 (5개 샘플)**: "만약 이순신 장군이 현대 무기를 사용했다면, 전황은 어떻게 바뀌었을까?", "이순신의 리더십 스타일을 MBTI로 분석한다면?" ...

| 질문 유형 | Top-k (비교) | Temperature (Grid-Search) | 예상 결과 (태그) | 결과 로그 |
| :--- | :--- | :--- | :--- | :--- |
| **사실 기반** | 1 vs 3 | 0.0, 0.2, 0.5, 0.8 | `accurate` / `verbose` | [결과 CSV 링크] |
| **요약** | 3 vs 5 | 0.0, 0.2, 0.5, 0.8 | `concise` / `missing_info` | [결과 CSV 링크] |
| **창의적/추론** | 5 vs 10 | 0.0, 0.2, 0.5, 0.8 | `insightful` / `off-topic` | [결과 CSV 링크] |

--- 