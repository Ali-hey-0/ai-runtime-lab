import json
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Span:
    span_id: str
    name: str
    kind: str  # "LLM", "TOOL", "MEMORY"
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    status: str = "OK"


class AgentTracer:
    """موتور ردیابی وقایع و محاسبه هزینه‌ها و گام‌های ایجنت"""

    def __init__(self, trace_id: str = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.spans: List[Span] = []

    def start_span(self, name: str, kind: str, attributes: Dict[str, Any] = None) -> Span:
        span = Span(
            span_id=str(uuid.uuid4())[:8],
            name=name,
            kind=kind,
            start_time=time.time(),
            attributes=attributes or {}
        )
        self.spans.append(span)
        return span

    def end_span(self, span: Span, status: str = "OK", extra_attributes: Dict[str, Any] = None):
        span.end_time = time.time()
        span.status = status
        if extra_attributes:
            span.attributes.update(extra_attributes)

    def get_trajectory_summary(self) -> Dict[str, Any]:
        total_duration = sum((s.end_time - s.start_time) for s in self.spans if s.end_time)
        tool_calls = [s.name for s in self.spans if s.kind == "TOOL"]
        total_tokens = sum(s.attributes.get("total_tokens", 0) for s in self.spans if s.kind == "LLM")

        return {
            "trace_id": self.trace_id,
            "total_spans": len(self.spans),
            "total_duration_sec": round(total_duration, 3),
            "total_tokens": total_tokens,
            "tool_trajectory": tool_calls
        }


class AgentEvaluator:
    """ارزیابی‌کننده عملکرد ایجنت (LLM-as-a-Judge Simulator)"""

    @staticmethod
    def evaluate_trajectory(actual_trajectory: List[str], optimal_trajectory: List[str]) -> Dict[str, Any]:
        """محاسبه شاخص کارایی مسیر (Trajectory Efficiency)"""
        n_optimal = len(optimal_trajectory)
        n_actual = len(actual_trajectory)

        if n_actual == 0:
            efficiency = 0.0
        else:
            efficiency = min(1.0, n_optimal / n_actual)

        # بررسی انحراف کامل از مسیر
        matched_steps = sum(1 for a, b in zip(actual_trajectory, optimal_trajectory) if a == b)
        step_accuracy = matched_steps / n_optimal if n_optimal > 0 else 0.0

        return {
            "trajectory_efficiency": round(efficiency, 2),
            "step_accuracy": round(step_accuracy, 2),
            "passed": efficiency >= 0.8 and step_accuracy == 1.0
        }


# --- تست سناریوی واقعی ---
if __name__ == "__main__":
    tracer = AgentTracer()

    # ۱. ثبت گام استدلال اول (LLM)
    span1 = tracer.start_span("Reasoning_Step_1", kind="LLM", attributes={"model": "gpt-4o"})
    time.sleep(0.05)  # شبیه‌سازی Latency
    tracer.end_span(span1, extra_attributes={"total_tokens": 350})

    # ۲. ثبت فراخوانی ابزار (Tool Execution)
    span2 = tracer.start_span("SQL_Query_Tool", kind="TOOL", attributes={"query": "SELECT * FROM users"})
    time.sleep(0.1)
    tracer.end_span(span2, status="OK")

    # ۳. ثبت گام استدلال دوم (LLM)
    span3 = tracer.start_span("Reasoning_Step_2", kind="LLM", attributes={"model": "gpt-4o"})
    time.sleep(0.04)
    tracer.end_span(span3, extra_attributes={"total_tokens": 200})

    # خلاصه Trace پردازش‌شده
    summary = tracer.get_trajectory_summary()
    print("--- Execution Trace Summary ---")
    print(json.dumps(summary, indent=2))

    # ارزیابی عملکرد مسیر علیه مسیر بهینه (Evals Check)
    optimal_path = ["SQL_Query_Tool"]
    eval_result = AgentEvaluator.evaluate_trajectory(
        actual_trajectory=summary["tool_trajectory"],
        optimal_trajectory=optimal_path
    )

    print("\n--- Evaluation (Evals) Results ---")
    print(json.dumps(eval_result, indent=2))

