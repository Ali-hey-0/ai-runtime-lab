from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ModelSpecs:
    name: str
    num_params_billions: float
    num_layers: int
    num_heads: int
    head_dim: int


class EdgeMemoryBudgetEngine:
    """موتور محاسبه و اعتبارسنجی بودجه RAM برای اجرای محلی ایجنت"""

    BYTES_PER_BIT = {
        "FP16": 2.0,
        "Q8_0": 1.0,
        "Q4_K_M": 0.55,  # میانگین بیت با احتساب متادیتای k-quant
        "Q2_K": 0.35,
    }

    def __init__(self, available_ram_gb: float):
        self.available_ram_gb = available_ram_gb

    def calculate_kv_cache_gb(self, specs: ModelSpecs, seq_len: int, kv_precision_bits: int = 16) -> float:
        """محاسبه حجم اشغالی KV Cache در حافظه"""
        bytes_per_elem = kv_precision_bits / 8.0
        total_bytes = 2 * specs.num_layers * specs.num_heads * specs.head_dim * seq_len * bytes_per_elem
        return total_bytes / (1024 ** 3)

    def evaluate_execution_feasibility(
        self, specs: ModelSpecs, quant_type: str, max_context: int
    ) -> Dict[str, Any]:
        if quant_type not in self.BYTES_PER_BIT:
            raise ValueError(f"Unsupported quantization: {quant_type}")

        # ۱. محاسبه حجم وزن‌های مدل
        weight_bytes = specs.num_params_billions * 1e9 * self.BYTES_PER_BIT[quant_type]
        weight_ram_gb = weight_bytes / (1024 ** 3)

        # ۲. محاسبه حجم KV Cache
        kv_ram_gb = self.calculate_kv_cache_gb(specs, seq_len=max_context, kv_precision_bits=16)

        # ۳. بودجه لایه اجرای Runtime (ضریب اطمینان برای llama.cpp و OS Overhead)
        runtime_overhead_gb = 0.5

        total_required_gb = weight_ram_gb + kv_ram_gb + runtime_overhead_gb
        is_safe = total_required_gb <= self.available_ram_gb

        return {
            "feasible": is_safe,
            "total_ram_required_gb": round(total_required_gb, 2),
            "breakdown": {
                "weights_gb": round(weight_ram_gb, 2),
                "kv_cache_gb": round(kv_ram_gb, 2),
                "overhead_gb": runtime_overhead_gb,
            },
            "status": "SAFE" if is_safe else "RISK_OF_OOM_KILL",
        }


# --- تست عملکرد ---
if __name__ == "__main__":
    # مشخصات مدل Llama-3-8B
    llama_8b = ModelSpecs(
        name="Llama-3-8B",
        num_params_billions=8.0,
        num_layers=32,
        num_heads=32,
        head_dim=128
    )

    # فرض: رم در دسترس در محیط لبه/ترموکس = 6 گیگابایت
    engine = EdgeMemoryBudgetEngine(available_ram_gb=6.0)

    # سناریو ۱: اجرای FP16 (غیرممکن)
    res1 = engine.evaluate_execution_feasibility(llama_8b, quant_type="FP16", max_context=4096)
    print(f"[SCENARIO 1 - FP16]: Feasible={res1['feasible']} | Status={res1['status']} | Needed={res1['total_ram_required_gb']} GB")

    # سناریو ۲: اجرای Q4_K_M (ممکن و ایمن)
    res2 = engine.evaluate_execution_feasibility(llama_8b, quant_type="Q4_K_M", max_context=4096)
    print(f"[SCENARIO 2 - Q4_K_M]: Feasible={res2['feasible']} | Status={res2['status']} | Needed={res2['total_ram_required_gb']} GB")
    print("Breakdown:", res2['breakdown'])

