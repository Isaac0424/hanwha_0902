"""예제 전반에서 재사용하는 추론 시간 측정 및 클라우드 대비 비용/전기요금 추정 유틸리티."""
import functools
import json
import time
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

import httpx
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult


def timed(label: str | None = None) -> Callable:
    """함수를 감싸서 실행 시간을 출력하는 데코레이터.

    LLM 호출뿐 아니라 체인 invoke, 일반 함수 어디에나 붙일 수 있다.
    네트워크 왕복을 포함한 wall-clock 시간을 잰다.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            name = label or func.__name__
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                print(f"[timed] {name}: {elapsed:.3f}s")

        return wrapper

    return decorator


class LatencyCallbackHandler(BaseCallbackHandler):
    """LangChain 콜백으로 LLM 호출 구간만 정확히 측정한다.

    `llm.invoke(question, config={"callbacks": [LatencyCallbackHandler()]})`
    처럼 넘기면, 체인/에이전트 내부 어디서 LLM이 몇 번 호출되든 자동으로 찍힌다.
    데코레이터와 달리 함수를 감쌀 필요가 없다는 점이 다르다.
    """

    def __init__(self) -> None:
        self._starts: dict[UUID, float] = {}

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], *, run_id: UUID, **kwargs: Any
    ) -> None:
        self._starts[run_id] = time.perf_counter()

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        self._starts[run_id] = time.perf_counter()

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        start = self._starts.pop(run_id, None)
        if start is not None:
            elapsed = time.perf_counter() - start
            print(f"[callback] LLM 호출 소요 시간: {elapsed:.3f}s")


def print_ollama_durations(response_metadata: dict[str, Any]) -> None:
    """ChatOllama 응답에 이미 들어있는 Ollama 서버 측 정밀 타이밍을 출력한다.

    Ollama API가 나노초 단위로 total/load/prompt_eval/eval duration을 돌려주므로,
    별도 측정 코드 없이도 순수 추론 시간(네트워크 왕복 제외)을 정확히 알 수 있다.
    """
    ns_to_s = 1e-9
    fields = ["total_duration", "load_duration", "prompt_eval_duration", "eval_duration"]
    for field in fields:
        if field in response_metadata:
            print(f"  {field}: {response_metadata[field] * ns_to_s:.3f}s")


# TODO: 이 파일이 더 커지면 타이밍 측정(위)과 비용/절약 추정(아래)을 각각
# utils_timing.py / utils_cost.py로 분리할 것. 지금 규모(약 200줄)에서는 안 쪼개도 됨.

# 공식 가격 API가 없어 커뮤니티가 유지하는 LiteLLM 가격표를 참고용으로 가져온다.
# 정확한 과금 용도가 아니라 "클라우드 API를 썼다면 얼마였을까"를 감 잡는 자기만족용 비교치다.
LITELLM_PRICE_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
)
PRICE_CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "outputs" / "price_cache.json"
PRICE_CACHE_TTL_SECONDS = 24 * 3600

# 네트워크 조회가 실패했을 때만 쓰는 최후 폴백값 (USD / 1M 토큰)
CLOUD_PRICE_PER_1M_TOKENS_FALLBACK = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}

GPU_TDP_WATT = 80  # RTX 2070 Max-Q 대략적 TDP. 실제 GPU에 맞게 조정할 것
ELECTRICITY_KRW_PER_KWH = 150  # 사용 지역 전기요금표 기준으로 조정할 것

SAVINGS_PATH = Path(__file__).resolve().parent.parent / "data" / "outputs" / "savings.json"


def _load_cloud_prices() -> dict[str, dict[str, float]]:
    """LiteLLM 커뮤니티 가격 JSON을 로컬에 캐싱(TTL 24h)해서 가져온다.

    캐시가 신선하면 네트워크 요청 없이 그대로 쓰고, 캐시가 없거나 오래됐으면 새로 받아
    캐싱한다. 요청이 실패하면(오프라인 등) 하드코딩된 폴백 표로 조용히 넘어간다.
    """
    if PRICE_CACHE_PATH.exists():
        age = time.time() - PRICE_CACHE_PATH.stat().st_mtime
        if age < PRICE_CACHE_TTL_SECONDS:
            try:
                return json.loads(PRICE_CACHE_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass  # 캐시가 깨졌으면 아래에서 새로 받는다

    try:
        resp = httpx.get(LITELLM_PRICE_URL, timeout=5.0)
        resp.raise_for_status()
        raw = resp.json()
    except (httpx.HTTPError, ValueError):
        return CLOUD_PRICE_PER_1M_TOKENS_FALLBACK

    prices: dict[str, dict[str, float]] = {}
    for model, info in raw.items():
        input_cost = info.get("input_cost_per_token")
        output_cost = info.get("output_cost_per_token")
        if input_cost is not None and output_cost is not None:
            prices[model] = {
                "input": input_cost * 1_000_000,
                "output": output_cost * 1_000_000,
            }

    if not prices:
        return CLOUD_PRICE_PER_1M_TOKENS_FALLBACK

    PRICE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRICE_CACHE_PATH.write_text(json.dumps(prices, ensure_ascii=False, indent=2), encoding="utf-8")
    return prices


def estimate_equivalent_cost_usd(
    usage_metadata: dict[str, Any], model: str = "gpt-4o-mini"
) -> float:
    """이 호출을 클라우드 API(`model`)로 했다면 들었을 비용(USD)을 추정한다.

    가격은 LiteLLM 커뮤니티 가격표(캐싱됨)에서 우선 찾고, 없으면 하드코딩된
    폴백값을 쓴다. 둘 다 없는 모델명이면 KeyError.
    """
    prices = _load_cloud_prices()
    price = prices.get(model) or CLOUD_PRICE_PER_1M_TOKENS_FALLBACK[model]
    return (
        usage_metadata.get("input_tokens", 0) / 1_000_000 * price["input"]
        + usage_metadata.get("output_tokens", 0) / 1_000_000 * price["output"]
    )


def estimate_electricity_cost_krw(eval_duration_ns: int) -> float:
    """생성 구간(eval_duration) 동안의 GPU 전력 소비를 전기요금(원)으로 추정한다."""
    hours = (eval_duration_ns / 1e9) / 3600
    kwh = GPU_TDP_WATT * hours / 1000
    return kwh * ELECTRICITY_KRW_PER_KWH


def record_savings(
    usage_metadata: dict[str, Any],
    response_metadata: dict[str, Any],
    model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    """이번 호출의 절약액을 계산해 data/outputs/savings.json 누적 기록에 더하고 요약을 출력한다.

    로컬 추론은 토큰당 과금이 없으므로, 클라우드 대비 절약액(USD)과 실제 전기요금(KRW)을
    서로 다른 통화 그대로 각각 누적한다 — 환율로 합산하지 않는다.

    TODO: 락 없이 읽기-수정-쓰기라서 여러 스크립트를 동시에 돌리면 카운트가 씹힐 수 있다.
    병렬 실행할 일이 생기면 filelock 등으로 보완할 것 (순차 실행 중엔 문제 없음).
    """
    equivalent_usd = estimate_equivalent_cost_usd(usage_metadata, model)
    electricity_krw = estimate_electricity_cost_krw(response_metadata.get("eval_duration", 0))

    SAVINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SAVINGS_PATH.exists():
        totals = json.loads(SAVINGS_PATH.read_text(encoding="utf-8"))
    else:
        totals = {}

    # 이전 스키마(예: total_tokens 없던 버전)로 저장된 파일도 그대로 이어서 누적하도록 보정.
    # total_tokens가 아예 없던 구버전 파일은 0이 아니라 input+output 누적치로 역산해서
    # 채워야 이번 호출분만 반영되는 식으로 누적이 끊기지 않는다.
    totals.setdefault("call_count", 0)
    totals.setdefault("input_tokens", 0)
    totals.setdefault("output_tokens", 0)
    if "total_tokens" not in totals:
        totals["total_tokens"] = totals["input_tokens"] + totals["output_tokens"]
    totals.setdefault("equivalent_cost_usd", 0.0)
    totals.setdefault("electricity_cost_krw", 0.0)

    call_input = usage_metadata.get("input_tokens", 0)
    call_output = usage_metadata.get("output_tokens", 0)
    call_total = usage_metadata.get("total_tokens", call_input + call_output)

    totals["call_count"] += 1
    totals["input_tokens"] += call_input
    totals["output_tokens"] += call_output
    totals["total_tokens"] += call_total
    totals["equivalent_cost_usd"] += equivalent_usd
    totals["electricity_cost_krw"] += electricity_krw
    totals["compared_model"] = model

    SAVINGS_PATH.write_text(json.dumps(totals, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"[savings] 이번 호출: 토큰 입력 {call_input} / 출력 {call_output} / 합계 {call_total} — "
        f"{model} 기준 약 ${equivalent_usd:.6f} 상당 / 전기요금 약 {electricity_krw:.4f}원"
    )
    print(
        f"[savings] 누적({totals['call_count']}회): "
        f"토큰 입력 {totals['input_tokens']} / 출력 {totals['output_tokens']} / "
        f"합계 {totals['total_tokens']} — 클라우드({model}) 대비 약 ${totals['equivalent_cost_usd']:.4f} "
        f"상당 / 전기요금 누적 약 {totals['electricity_cost_krw']:.2f}원"
    )
    return totals
