"""
Failure / Retry / Idempotency with lease-based in-flight locks.

Prevents ambiguous "in-progress" state after a crash between side-effect
dispatch and local commit: stale leases expire to RETRY_READY on recovery.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


class OpStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    RETRY_READY = "RETRY_READY"
    FAILED = "FAILED"


# Default lease TTL for in-flight idempotent ops (seconds).
DEFAULT_LEASE_TTL_S = 30.0
STATE_FILE = Path(__file__).resolve().parent / "idempotency_state.json"


class IdempotencyStore:
    """Durable-ish store for idempotency keys with TTL leases."""

    def __init__(self, path: Path = STATE_FILE, lease_ttl_s: float = DEFAULT_LEASE_TTL_S):
        self.path = path
        self.lease_ttl_s = lease_ttl_s
        self._data: dict[str, dict[str, Any]] = self._load()

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _persist(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get(self, key: str) -> Optional[dict[str, Any]]:
        return self._data.get(key)

    def reconcile(self, now: Optional[float] = None) -> list[str]:
        """
        On recovery: expire stale IN_PROGRESS leases → RETRY_READY.
        Returns keys that were marked RETRY_READY.
        """
        now = time.time() if now is None else now
        recovered: list[str] = []
        for key, rec in list(self._data.items()):
            if rec.get("status") != OpStatus.IN_PROGRESS.value:
                continue
            lease_until = float(rec.get("lease_until", 0))
            if now >= lease_until:
                rec["status"] = OpStatus.RETRY_READY.value
                rec["lease_until"] = None
                rec["recovered_at"] = now
                recovered.append(key)
                print(
                    f"[RECONCILE] Key {key} lease expired "
                    f"-> {OpStatus.RETRY_READY.value} (safe to retry)"
                )
        if recovered:
            self._persist()
        return recovered

    def try_acquire(self, key: str, now: Optional[float] = None) -> tuple[bool, Optional[Any]]:
        """
        Acquire or re-acquire a lease for `key`.
        Returns (acquired, cached_result_if_completed).
        """
        now = time.time() if now is None else now
        # Always reconcile before acquire so crash leftovers become retryable.
        self.reconcile(now=now)

        rec = self._data.get(key)
        if rec is None:
            self._data[key] = {
                "status": OpStatus.IN_PROGRESS.value,
                "lease_until": now + self.lease_ttl_s,
                "result": None,
                "heartbeat_at": now,
            }
            self._persist()
            return True, None

        status = rec.get("status")
        if status == OpStatus.COMPLETED.value:
            return False, rec.get("result")

        if status == OpStatus.FAILED.value:
            # Terminal failure — do not re-dispatch without explicit reset.
            return False, None

        if status == OpStatus.IN_PROGRESS.value:
            lease_until = float(rec.get("lease_until") or 0)
            if now < lease_until:
                # Another worker still holds a live lease.
                print(f"[LEASE HELD] Key {key} in-progress until {lease_until:.0f}")
                return False, None
            # Should have been reconciled; treat as retry-ready fallthrough.
            status = OpStatus.RETRY_READY.value

        if status == OpStatus.RETRY_READY.value:
            rec["status"] = OpStatus.IN_PROGRESS.value
            rec["lease_until"] = now + self.lease_ttl_s
            rec["heartbeat_at"] = now
            self._persist()
            return True, None

        return False, None

    def heartbeat(self, key: str, now: Optional[float] = None) -> None:
        """Extend lease while work is still running (long activities)."""
        now = time.time() if now is None else now
        rec = self._data.get(key)
        if not rec or rec.get("status") != OpStatus.IN_PROGRESS.value:
            return
        rec["lease_until"] = now + self.lease_ttl_s
        rec["heartbeat_at"] = now
        self._persist()

    def complete(self, key: str, result: Any, now: Optional[float] = None) -> None:
        now = time.time() if now is None else now
        self._data[key] = {
            "status": OpStatus.COMPLETED.value,
            "lease_until": None,
            "result": result,
            "completed_at": now,
        }
        self._persist()

    def mark_failed(self, key: str, error: str, now: Optional[float] = None) -> None:
        now = time.time() if now is None else now
        self._data[key] = {
            "status": OpStatus.FAILED.value,
            "lease_until": None,
            "result": None,
            "error": error,
            "failed_at": now,
        }
        self._persist()

    def mark_retry_ready(self, key: str, now: Optional[float] = None) -> None:
        """Release lease after transient failure so a later attempt can retry."""
        now = time.time() if now is None else now
        rec = self._data.get(key) or {}
        rec.update(
            {
                "status": OpStatus.RETRY_READY.value,
                "lease_until": None,
                "retry_ready_at": now,
            }
        )
        self._data[key] = rec
        self._persist()


def make_idempotency_key(task_id: str, step_name: str) -> str:
    return hashlib.sha256(f"{task_id}:{step_name}".encode()).hexdigest()[:12]


def execute_idempotent_activity(
    task_id: str,
    step_name: str,
    action_fn: Callable[[str], Any],
    max_retries: int = 3,
    store: Optional[IdempotencyStore] = None,
    lease_ttl_s: float = DEFAULT_LEASE_TTL_S,
):
    """
    Run an activity under an idempotency key with lease-based in-flight locks.

    Crash window addressed:
      external side-effect succeeds → process dies before local commit
    On restart, reconcile() expires the lease → RETRY_READY; caller retries
    with the same key so the downstream can de-dupe via Idempotency-Key.
    """
    store = store or IdempotencyStore(lease_ttl_s=lease_ttl_s)
    idempotency_key = make_idempotency_key(task_id, step_name)

    # Recovery pass before any attempt.
    store.reconcile()

    base_delay = 0.5
    last_error: Optional[BaseException] = None

    for attempt in range(max_retries):
        acquired, cached = store.try_acquire(idempotency_key)
        if cached is not None:
            print(f"[IDEMPOTENT HIT] Key {idempotency_key} already COMPLETED — returning cache")
            return cached
        if not acquired:
            # Live lease held by another worker, or terminal FAILED.
            rec = store.get(idempotency_key) or {}
            if rec.get("status") == OpStatus.FAILED.value:
                raise RuntimeError(
                    f"Idempotency key {idempotency_key} is FAILED: {rec.get('error')}"
                )
            # Wait for lease to expire rather than blind parallel replay.
            sleep_time = min(lease_ttl_s, base_delay * (2 ** attempt))
            print(
                f"[WAIT LEASE] Key {idempotency_key} locked; "
                f"backing off {sleep_time:.2f}s (attempt {attempt + 1})"
            )
            time.sleep(sleep_time)
            continue

        try:
            print(f"[ATTEMPT {attempt + 1}] Executing with Key: {idempotency_key}")
            # Optional heartbeat mid-flight for long actions:
            # store.heartbeat(idempotency_key)
            result = action_fn(idempotency_key)
            # Commit local state only after successful side-effect return.
            store.complete(idempotency_key, result)
            return result

        except Exception as e:
            last_error = e
            if attempt == max_retries - 1:
                store.mark_failed(idempotency_key, str(e))
                print(f"[PERMANENT FAILURE] Max retries reached for key {idempotency_key}.")
                raise

            # Transient: free the lease so recovery/retry is unambiguous.
            store.mark_retry_ready(idempotency_key)
            sleep_time = random.uniform(0, min(8.0, base_delay * (2 ** attempt)))
            print(f"[TRANSIENT ERROR] {e} -> Retrying in {sleep_time:.2f}s...")
            time.sleep(sleep_time)

    assert last_error is not None
    raise last_error


if __name__ == "__main__":
    # Demo: simulate crash leaving a stale IN_PROGRESS lease, then recover.
    demo_store = IdempotencyStore(
        path=Path(__file__).resolve().parent / "idempotency_state_demo.json",
        lease_ttl_s=1.0,
    )
    key = make_idempotency_key("task-demo", "charge_card")
    # Plant a stale in-flight record (crash after API call, before commit).
    demo_store._data[key] = {
        "status": OpStatus.IN_PROGRESS.value,
        "lease_until": time.time() - 5,  # already expired
        "result": None,
        "heartbeat_at": time.time() - 60,
    }
    demo_store._persist()
    print("[DEMO] Stale IN_PROGRESS planted; sleeping past TTL...")
    time.sleep(0.1)
    recovered = demo_store.reconcile()
    assert key in recovered, "stale lease should become RETRY_READY"
    print(f"[DEMO] Reconciled keys: {recovered}")

    def charge(_k: str) -> str:
        return "charged_once"

    out = execute_idempotent_activity(
        "task-demo", "charge_card", charge, store=demo_store, lease_ttl_s=1.0
    )
    print(f"[DEMO] Result: {out}")
    # Second call must hit cache, not re-charge.
    out2 = execute_idempotent_activity(
        "task-demo", "charge_card", charge, store=demo_store, lease_ttl_s=1.0
    )
    assert out2 == out
    print("[DEMO] Idempotent re-entry OK")
