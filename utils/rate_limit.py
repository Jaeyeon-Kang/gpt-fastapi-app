import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException
import config

# 간단한 메모리 기반 카운터 (무료 호스팅 환경 가정)
# 프로세스 재시작 시 초기화됨. 비용/남용 1차 방어용.
_daily_counts: Dict[Tuple[str, str], Tuple[int, float]] = {}
_burst_counts: Dict[Tuple[str, str], Tuple[int, float]] = {}


def _now() -> float:
    return time.time()


def _key(req: Request, name: str, session_id: Optional[str]) -> Tuple[str, str]:
    # 세션이 있으면 세션 기준, 없으면 IP 기준
    ip = req.client.host if req.client else "0.0.0.0"
    return (name, session_id or ip)


def check_limits(req: Request, name: str, daily_limit: int, burst_limit: int, session_id: Optional[str] = None):
    global _daily_counts, _burst_counts
    now = _now()
    dk = _key(req, name + ":daily", session_id)
    bk = _key(req, name + ":burst", session_id)

    # 일일 윈도우 처리
    d_count, d_start = _daily_counts.get(dk, (0, now))
    if now - d_start >= config.RATE_WINDOW_SECONDS:
        d_count, d_start = 0, now
    d_count += 1
    _daily_counts[dk] = (d_count, d_start)

    # 버스트 윈도우(1분 등)
    b_count, b_start = _burst_counts.get(bk, (0, now))
    if now - b_start >= config.BURST_WINDOW_SECONDS:
        b_count, b_start = 0, now
    b_count += 1
    _burst_counts[bk] = (b_count, b_start)

    if d_count > daily_limit:
        ttl = int(config.RATE_WINDOW_SECONDS - (now - d_start))
        raise HTTPException(status_code=429, detail=f"일일 요청 제한을 초과했습니다. {ttl}초 후에 다시 시도하세요.")
    if b_count > burst_limit:
        ttl = int(config.BURST_WINDOW_SECONDS - (now - b_start))
        raise HTTPException(status_code=429, detail=f"짧은 시간 내 요청이 너무 많습니다. {ttl}초 후에 다시 시도하세요.")