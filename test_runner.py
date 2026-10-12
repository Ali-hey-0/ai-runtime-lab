import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PHASE_SCRIPTS = [
    ("Phase 01: FSM", "fsm/fsm.py"),
    ("Phase 02: Durable Execution", "durable_execution/durable_execution.py"),
    ("Phase 03: Retry & Idempotency", "Failure-Retry-Idempotency/Failure-Retry-Idempotency.py"),
    ("Phase 04: DAG Orchestration", "dag/dag.py"),
    ("Phase 05: Agent Runtime", "agent-runtime/agent-runtime.py"),
    ("Phase 06: Model Routing", "model-routing/model-routing.py"),
    ("Phase 07: Inference KV Cache", "Inference-KV-Cache/Inference-KV-Cache.py"),
    ("Phase 08: RAG Context Management", "RAG-Context-Management/RAG-Context-Management.py"),
    ("Phase 09: Memory Systems", "Memory-Systems/Memory-Systems.py"),
    ("Phase 10: Multi-Agent Handoff", "Multi-Agent-Router-Handoff-Engine/Multi-Agent-Router-Handoff-Engine.py"),
    ("Phase 11: Security & Sandboxing", "Security-Sandboxing-Safety/Security-Sandboxing-Safety.py"),
    ("Phase 12: Observability Tracing", "Observability-Tracing-Evaluation/Observability-Tracing-Evaluation.py"),
    ("Phase 13: Observability Eval Engine", "Observability-Eval-Engine/Observability-Eval-Engine.py"),
]

def run_phase(name: str, rel_path: str) -> bool:
    script_path = ROOT / rel_path
    if not script_path.exists():
        print(f"[-] {name:<40} : MISSING ({rel_path})")
        return False
    
    # Phase 2 is an intentional power failure simulation on first crash check
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=script_path.parent,
        capture_output=True,
        text=True
    )
    
    # If phase 2, it is designed to crash on missing step_3_db, verify expected crash output
    if "durable_execution" in rel_path:
        passed = (proc.returncode == 1 and "[CRASH] Power failure before step 3!" in proc.stdout) or proc.returncode == 0
    else:
        passed = proc.returncode == 0
        
    status = "PASSED" if passed else f"FAILED (exit {proc.returncode})"
    print(f"[{'x' if passed else ' '}] {name:<40} : {status}")
    if not passed:
        if proc.stderr:
            print("    Error:", proc.stderr.strip()[:300])
        elif proc.stdout:
            print("    Output:", proc.stdout.strip()[:300])
    return passed

def main():
    print("==================================================")
    print("      AI Runtime Lab - Verification Suite         ")
    print("==================================================")
    all_passed = True
    for name, rel_path in PHASE_SCRIPTS:
        if not run_phase(name, rel_path):
            all_passed = False
    print("==================================================")
    if all_passed:
        print("All 13 runnable phases verified successfully! [OK]")
        sys.exit(0)
    else:
        print("Some phases failed verification! [FAIL]")
        sys.exit(1)

if __name__ == '__main__':
    main()
