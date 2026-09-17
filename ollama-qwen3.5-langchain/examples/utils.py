"""예제 전반에서 재사용하는 추론 시간 측정 유틸리티."""
import functools
import time
from typing import Any, Callable
from uuid import UUID

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
