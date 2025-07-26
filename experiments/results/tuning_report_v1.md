# RAG Experiment Tuning Report v1

**Generated**: 2025-07-26 17:44:35  
**Total Experiments**: 90  
**Data Source**: 5f311582... (latest grid search)

## Executive Summary

- **Best Average Recall@5**: 0.762
- **Best Average F1 Score**: 0.762
- **Average Latency**: 1274.8ms
- **Average Cost**: $0.0541
- **Perfect Scores**: 42 experiments
- **Failed Experiments**: 3 experiments

## Top 5 Parameter Combinations

| Rank | Chunk | Top-k | Temp | Recall@5 | F1 | Latency(ms) | Cost(cents) |
|------|-------|-------|------|----------|----|-------------|-------------|
| 1 | 256.0 | 3.0 | 0.2 | 1.000 | 1.000 | 1092.0 | 0.0284 |
| 2 | 256.0 | 3.0 | 0.2 | 1.000 | 1.000 | 824.3 | 0.0237 |
| 3 | 256.0 | 3.0 | 0.2 | 1.000 | 1.000 | 909.7 | 0.0191 |
| 4 | 256.0 | 3.0 | 0.5 | 1.000 | 1.000 | 1101.8 | 0.0264 |
| 5 | 256.0 | 3.0 | 0.5 | 1.000 | 1.000 | 872.5 | 0.0237 |

## Key Insights

- **Chunk size 512** shows better average recall than 256
- **Top-k=3** performs best on average
- **Temperature=0.2** shows best average performance
- **Most cost-efficient**: chunk=256, k=3

## Performance Analysis

### Best Parameters
**Optimal Configuration**: chunk=256.0, k=3.0, temp=0.2

**Why this works best**:
- Achieves 100.0% recall with 100.0% F1 score
- Cost-effective at $0.0284 per query
- Reasonable latency of 1092ms

### Cost-Performance Trade-off
- **Most Expensive**: $0.1137 (chunk=512, k=8)
- **Cheapest**: $0.0191 (chunk=256, k=3)
- **Best Value**: $0.0284 with 100.0% recall

## Recommendations

1. **Production Use**: chunk=256.0, k=3.0, temp=0.2
2. **Cost Optimization**: Consider chunk=256, k=3 for high-volume scenarios
3. **Performance Focus**: Use chunk=256, k=3 for critical applications

## Next Steps

- Implement the recommended parameters in production
- Monitor real-world performance vs. experimental results
- Consider A/B testing different configurations
- Plan for scaling experiments with larger datasets

---

## Git 태그 남기기

### 8단계: 실험 완료 태그 생성

**명령어**
```bash
git add .
git commit -m "feat: Complete RAG experiment automation with tuning report

- Full grid search: 90 experiments completed
- Analysis: tuning_report_v1.md generated
- Visualizations: performance_analysis.png created
- Best parameters identified and recommendations made"
git tag -a v1.0-experiment -m "RAG experiment automation v1.0 completed"
```

**설명**
- **git add .**: 모든 변경사항 스테이징
- **git commit**: 실험 완료 커밋 생성
- **git tag**: v1.0-experiment 태그 생성 (나중에 찾기 쉽게)

---

**이렇게 하면:**
- 실험 완료 시점이 명확히 기록됨
- 나중에 "v1.0-experiment" 태그로 언제든 찾을 수 있음
- 포트폴리오에서 "이때 실험을 완료했다"는 증거가 됨

---

**실행해볼까?  
아니면 다른 방법으로 기록하고 싶어?**
