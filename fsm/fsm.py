import json
from enum import StrEnum
from pathlib import Path


class State(StrEnum):
    INIT = "INIT"
    READING = "READING"
    ANALYZING = "ANALYZING"
    DONE = "DONE"
    FAILED = "FAILED"


class PersistentFSM:
    TRANSITIONS = {
        State.INIT: {State.READING},
        State.READING: {State.ANALYZING, State.FAILED},
        State.ANALYZING: {State.DONE, State.FAILED},
        State.DONE: set(),
        State.FAILED: set(),
    }

    def __init__(self, db_path: str = "checkpoint.json"):
        self.db_path = Path(db_path)
        self.state = State.INIT
        self.retries = 0
        self.recover()  # ۱. بازیابی خودکار در صورت کرش قبلی

    def recover(self) -> None:
        if self.db_path.exists():
            data = json.loads(self.db_path.read_text())
            self.state = State(data["state"])
            self.retries = data["retries"]

    def _checkpoint(self) -> None:
        """ذخیره سنکرون روی دیسک پیش از ادامه اجرا"""
        self.db_path.write_text(json.dumps({"state": self.state.value, "retries": self.retries}))

    def transition_to(self, new_state: State, guard: bool = True) -> None:
        # ۲. Invariant: انتقال خارج از ماتریس ممنوع
        if new_state not in self.TRANSITIONS[self.state]:
            raise ValueError(f"Illegal transition: {self.state} -> {new_state}")

        # ۳. Guard Condition Evaluation
        if not guard:
            raise PermissionError(f"Guard failed for target state: {new_state}")

        self.state = new_state
        self._checkpoint()  # اول دیسک به‌روز می‌شود، سپس State برنامه


# --- تست عملکرد و Crash Simulation ---
if __name__ == "__main__":
    fsm = PersistentFSM()
    print(f"[BOOT] Current state: {fsm.state}")

    if fsm.state == State.INIT:
        fsm.transition_to(State.READING)
        print(f"[TRANSITION] Moved to: {fsm.state}")

        # شبیه‌سازی کرش ناگهانی (قطع برق) وسط کار
        print("[CRASH] Simulating power loss...")
        exit(1)

