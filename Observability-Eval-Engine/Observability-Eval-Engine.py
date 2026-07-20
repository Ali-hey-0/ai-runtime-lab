import time
from dataclasses import dataclass, field
from typing import List, Dict, Any


# ۱. ساختار داده‌ای Spans برای Tracing دقیق
@dataclass
class Span:
    name: str
    input_data: Any
    output_data: Any = None
    duration_ms: float = 0.0
    tokens_used: int = 0


@dataclass
class Trace:
    trace_id: str
    spans: List[Span] = field(default_factory=list)

    def total_tokens(self) -> int:
        return sum(s.tokens_used for s in self.spans)


class AgentTracer:
    def __init__(self, trace_id: str):
        self.trace = Trace(trace_id=trace_id)

    def start_span(self, name: str, input_data: Any):
        return SpanTracker(self.trace, name, input_data)


class SpanTracker:
    def __init__(self, trace: Trace, name: str, input_data: Any):
        self.trace = trace
        self.span = Span(name=name, input_data=input_data)
        self.start_time = 0

    def __enter__(self):
        self.start_time = time.time()
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.span.duration_ms = (time.time() - self.start_time) * 1000
        self.trace.spans.append(self.span)


# ۲. موتور ارزیابی (Eval Harness)
class EvalEngine:
    @staticmethod
    def evaluate_run(trace: Trace, final_output: str) -> Dict[str, Any]:
        # Rule 1: Deterministic Check - Schema/Length
        length_ok = len(final_output) > 5

        # Rule 2: Token Budget Check
        budget_ok = trace.total_tokens() <= 500

        # Rule 3: LLM-as-a-Judge (شبیه‌سازی‌شده)
        faithfulness_score = 0.95 if "valid" in final_output.lower() else 0.40

        return {
            "passed": length_ok and budget_ok and (faithfulness_score > 0.7),
            "metrics": {
                "total_tokens": trace.total_tokens(),
                "spans_count": len(trace.spans),
                "faithfulness": faithfulness_score
            }
        }


# --- تست عملکرد ---
if __name__ == "__main__":
    tracer = AgentTracer(trace_id="run_9981")

    # شبیه‌سازی اجرای یک Span (مثلاً فراخوانی LLM)
    with tracer.start_span("LLM_Call", input_data="Summarize text") as span:
        time.sleep(0.05)  # شبیه‌سازی Latency
        span.output_data = "Valid Summary Output"
        span.tokens_used = 120

    # ارزیابی خروجی
    results = EvalEngine.evaluate_run(tracer.trace, final_output="Valid Summary Output")
    print(f"[TRACE AUDIT] Total Tokens: {tracer.trace.total_tokens()} | Total Spans: {len(tracer.trace.spans)}")
    print(f"[EVAL RESULTS] Passed: {results['passed']} | Metrics: {results['metrics']}")

