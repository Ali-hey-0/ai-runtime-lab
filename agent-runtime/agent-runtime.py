import json
from dataclasses import dataclass
from typing import Dict, Any, Callable


# ۱. ساختار شفاف اکشن‌های LLM
@dataclass
class AgentAction:
    tool_name: str
    args: Dict[str, Any]


class AgentRuntime:
    def __init__(self, fsm_engine, tools: Dict[str, Callable], max_steps: int = 5):
        self.fsm = fsm_engine
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def _mock_llm_decide(self, step: int) -> AgentAction:
        """شبیه‌سازی موتور احتمالی LLM"""
        if step == 1:
            return AgentAction(tool_name="read_file", args={"path": "data.txt"})
        elif step == 2:
            return AgentAction(tool_name="analyze_text", args={"content": "data_ok"})
        return AgentAction(tool_name="finish", args={"result": "Success"})

    def run(self, initial_input: str):
        print(f"[RUNTIME] Starting agent run for task: '{initial_input}'")
        
        for step in range(1, self.max_steps + 1):
            print(f"\n--- ReAct Step {step} ---")
            
            # گام ۱: دریافت تصمیم از LLM
            action = self._mock_llm_decide(step)
            print(f"[LLM INTENT] Proposed Tool: '{action.tool_name}' with args: {action.args}")

            # گام ۲: چک کردن Guardrail و وضعیت FSM
            if action.tool_name == "finish":
                self.fsm.transition_to("DONE")
                print("[RUNTIME] Task Completed Successfully.")
                return "DONE"

            # گام ۳: اعتبارسنجی ابزار
            if action.tool_name not in self.tools:
                print(f"[GUARD FAIL] Unknown tool: {action.tool_name}")
                continue

            # گام ۴: اجرای ابزار در لایه ایمن (Activity Execution)
            try:
                # تغییر وضعیت FSM بر اساس کار
                if action.tool_name == "read_file":
                    self.fsm.transition_to("READING")
                elif action.tool_name == "analyze_text":
                    self.fsm.transition_to("ANALYZING")

                result = self.tools[action.tool_name](**action.args)
                print(f"[TOOL OUTPUT] Result: {result}")
                
                # ثبت در حافظه کوتاه مدت جهت Replay/Context
                self.history.append({"step": step, "action": action.tool_name, "result": result})

            except Exception as e:
                print(f"[RUNTIME ERROR] Tool execution failed: {e}")
                self.fsm.transition_to("FAILED")
                break

        print("[RUNTIME EXHAUSTED] Max steps reached without completion.")


# --- تست عملکرد Runtime ---
if __name__ == "__main__":
    from types import SimpleNamespace

    # شبیه‌سازی FSM ساده
    fsm = SimpleNamespace(
        state="INIT", 
        transition_to=lambda s: print(f"[FSM STATE CHANGE] -> {s}")
    )

    # تعریف ابزارهای مجاز در سیستم (Deterministic Tools)
    tool_registry = {
        "read_file": lambda path: f"Content of {path}",
        "analyze_text": lambda content: f"Analysis of {content}"
    }

    # اجرا
    runtime = AgentRuntime(fsm_engine=fsm, tools=tool_registry)
    runtime.run("Analyze project files")

