from enum import StrEnum
from dataclasses import dataclass
from typing import Callable, Dict, Any


class ModelTier(StrEnum):
    FAST_SLM = "FAST_SLM"       # ارزان و سریع (e.g., Llama-8B / Flash)
    HEAVY_LLM = "HEAVY_LLM"     # گران و تفکر عمیق (e.g., Sonnet / GPT-4o)


@dataclass
class RouteDecision:
    selected_tier: ModelTier
    reason: str


class ModelRouter:
    """روتر بر پایه قواعد سریع و تحلیل ساختار ورودی"""

    @staticmethod
    def route(prompt: str, requires_complex_json: bool = False) -> RouteDecision:
        # ۱. Invariants & Rule-based check
        if requires_complex_json or len(prompt) > 2000:
            return RouteDecision(
                selected_tier=ModelTier.HEAVY_LLM,
                reason="High context length or complex schema requirement."
            )

        # ۲. Heuristic check (کلمات کلیدی استدلال پیچیده)
        complex_keywords = {"proof", "refactor", "architect", "math", "analyze"}
        words = set(prompt.lower().split())
        
        if len(words.intersection(complex_keywords)) > 0:
            return RouteDecision(
                selected_tier=ModelTier.HEAVY_LLM,
                reason="Complex reasoning keywords detected."
            )

        # ۳. Default to fast/cheap tier
        return RouteDecision(
            selected_tier=ModelTier.FAST_SLM,
            reason="Simple task matched lightweight heuristic."
        )


class RouterExecutionEngine:
    """موتور اجرا همراه با الگوی Fallback Cascading"""

    def __init__(self, providers: Dict[ModelTier, Callable]):
        self.providers = providers

    def execute_with_fallback(self, prompt: str, decision: RouteDecision) -> Any:
        primary_tier = decision.selected_tier
        fallback_tier = (
            ModelTier.HEAVY_LLM if primary_tier == ModelTier.FAST_SLM else ModelTier.FAST_SLM
        )

        # تلاش اول: مدل انتخاب‌شده توسط روتر
        try:
            print(f"[ROUTER] Directing to '{primary_tier.value}' | Reason: {decision.reason}")
            return self.providers[primary_tier](prompt)
        except Exception as e:
            print(f"[ROUTER FALLBACK] '{primary_tier.value}' failed ({e}). Escalating to '{fallback_tier.value}'...")
            # تلاش دوم: Fallback به مدل جایگزین
            return self.providers[fallback_tier](prompt)


# --- تست عملکرد ---
if __name__ == "__main__":
    # شبیه‌سازی ارائه دهندگان مدل
    def mock_slm(p):
        if "fail" in p:
            raise RuntimeError("SLM Rate Limit Exceeded")
        return f"SLM Output for: {p}"

    def mock_heavy(p):
        return f"Heavy LLM Detailed Output for: {p}"

    providers_map = {
        ModelTier.FAST_SLM: mock_slm,
        ModelTier.HEAVY_LLM: mock_heavy
    }

    engine = RouterExecutionEngine(providers_map)

    # سناریو ۱: درخواست ساده
    d1 = ModelRouter.route("Hello, classify this text")
    print("Result 1:", engine.execute_with_fallback("Hello, classify this text", d1))
    print("-" * 50)

    # سناریو ۲: درخواست پیچیده
    d2 = ModelRouter.route("Analyze and refactor this architecture")
    print("Result 2:", engine.execute_with_fallback("Analyze and refactor this architecture", d2))
    print("-" * 50)

    # سناریو ۳: بروز خطا در مدل ساده و اجرای Fallback
    d3 = ModelRouter.route("Simple text fail_test")
    print("Result 3:", engine.execute_with_fallback("Simple text fail_test", d3))

