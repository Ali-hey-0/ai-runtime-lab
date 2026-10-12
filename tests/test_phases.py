import sys
import subprocess
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PHASES = [
    ("fsm/fsm.py", False),
    ("durable_execution/durable_execution.py", True),
    ("Failure-Retry-Idempotency/Failure-Retry-Idempotency.py", False),
    ("dag/dag.py", False),
    ("agent-runtime/agent-runtime.py", False),
    ("model-routing/model-routing.py", False),
    ("Inference-KV-Cache/Inference-KV-Cache.py", False),
    ("RAG-Context-Management/RAG-Context-Management.py", False),
    ("Memory-Systems/Memory-Systems.py", False),
    ("Multi-Agent-Router-Handoff-Engine/Multi-Agent-Router-Handoff-Engine.py", False),
    ("Security-Sandboxing-Safety/Security-Sandboxing-Safety.py", False),
    ("Observability-Tracing-Evaluation/Observability-Tracing-Evaluation.py", False),
    ("Observability-Eval-Engine/Observability-Eval-Engine.py", False),
]

@pytest.mark.parametrize("script_rel,is_crash_simulation", PHASES)
def test_phase_execution(script_rel: str, is_crash_simulation: bool):
    script_path = ROOT / script_rel
    assert script_path.exists(), f"Phase script {script_rel} must exist"

    # Clean test artifacts
    log_file = script_path.parent / "execution_log.json"
    if log_file.exists():
        log_file.unlink()

    proc = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=script_path.parent,
        capture_output=True,
        text=True
    )

    if is_crash_simulation:
        assert proc.returncode in (0, 1)
        if proc.returncode == 1:
            assert "[CRASH] Power failure before step 3!" in proc.stdout
    else:
        assert proc.returncode == 0, f"Error in {script_rel}: {proc.stderr}"
