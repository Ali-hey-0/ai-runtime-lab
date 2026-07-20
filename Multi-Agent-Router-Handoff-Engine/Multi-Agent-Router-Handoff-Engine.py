from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class AgentResponse:
    content: str
    next_agent: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)


class Agent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        raise NotImplementedError


# --- ایجنت‌های تخصصی ---

class TriageAgent(Agent):
    """ایجنت تشخیص و ارجاع اولیه"""
    def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        task = payload.get("task", "")
        print(f"[{self.name}] Analyzing task: '{task}'")
        
        if "code" in task.lower() or "bug" in task.lower():
            return AgentResponse(
                content="Task classified as Coding.",
                next_agent="CoderAgent",
                payload={"code_snippet": payload.get("task_data", "")}
            )
        return AgentResponse(content="Task unknown or completed.", next_agent=None)


class CoderAgent(Agent):
    """ایجنت تخصصی کدنویسی"""
    def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        snippet = payload.get("code_snippet", "")
        print(f"[{self.name}] Fixing bug in snippet: '{snippet}'")
        
        # شبیه‌سازی ارجاع به ایجنت ارزیاب (Reviewer)
        return AgentResponse(
            content="Fixed code snippet.",
            next_agent="ReviewerAgent",
            payload={"fixed_code": f"def safe_func(): return '{snippet}'"}
        )


class ReviewerAgent(Agent):
    """ایجنت ارزیابی و تأیید نهایی"""
    def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        fixed_code = payload.get("fixed_code", "")
        print(f"[{self.name}] Reviewing code: '{fixed_code}'")
        
        # اتمام کار - بدون ارجاع بعدی
        return AgentResponse(
            content=f"APPROVED: {fixed_code}",
            next_agent=None
        )


# --- موتور ارکستریتور Swarm ---

class SwarmOrchestrator:
    def __init__(self, agents: List[Agent], max_handoffs: int = 5):
        self.agents: Dict[str, Agent] = {a.name: a for a in agents}
        self.max_handoffs = max_handoffs

    def run(self, start_agent_name: str, initial_payload: Dict[str, Any]) -> str:
        current_agent_name = start_agent_name
        current_payload = initial_payload
        handoff_history = []

        for step in range(self.max_handoffs):
            if current_agent_name not in self.agents:
                raise RuntimeError(f"Unknown agent: {current_agent_name}")

            # ۱. چک کردن حلقه ارجاع (Loop Detection)
            if current_agent_name in handoff_history[-2:]:
                raise RuntimeError(f"[SWARM CRASH] Ping-pong loop detected on '{current_agent_name}'!")

            handoff_history.append(current_agent_name)
            agent = self.agents[current_agent_name]

            # ۲. اجرای ایجنت با کانتکست ایزوله‌شده
            print(f"\n---> Step {step + 1}: Executing {current_agent_name}")
            response = agent.execute(current_payload)

            # ۳. بررسی وضعیت Handoff
            if not response.next_agent:
                print(f"[SWARM SUCCESS] Workflow terminated gracefully by {current_agent_name}.")
                return response.content

            # ۴. انتقال کنترل و پاک‌سازی کانتکست غیرضروری
            current_agent_name = response.next_agent
            current_payload = response.payload

        raise RuntimeError("[SWARM EXHAUSTED] Max handoffs budget exceeded.")


# --- تست عملکرد ---
if __name__ == "__main__":
    swarm_agents = [
        TriageAgent("TriageAgent", "Route tasks"),
        CoderAgent("CoderAgent", "Write code"),
        ReviewerAgent("ReviewerAgent", "Verify code")
    ]

    orchestrator = SwarmOrchestrator(agents=swarm_agents, max_handoffs=5)
    
    # شروع سناریو
    final_result = orchestrator.run(
        start_agent_name="TriageAgent",
        initial_payload={"task": "Fix a code bug", "task_data": "val = 1/0"}
    )
    print(f"\n[FINAL OUTPUT]: {final_result}")

