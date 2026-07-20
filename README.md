<div align="center">

# 🧠 AI Runtime Lab

### Engineering Deterministic Systems Around Non-Deterministic Models

*A hands-on curriculum and reference implementation for building production-grade agentic AI systems — from state machines to multi-agent swarms.*

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#license)
[![Status](https://img.shields.io/badge/Status-Active%20Learning%20Lab-orange?style=flat-square)](#roadmap--progress)
[![Phases](https://img.shields.io/badge/Phases-14%20%2F%2017-blue?style=flat-square)](#-the-14-phases)

[Philosophy](#-core-philosophy) •
[Architecture](#-system-architecture) •
[Phases](#-the-14-phases) •
[Repository Map](#-repository-map) •
[Roadmap](#-roadmap--progress)

</div>

---

## 📖 About This Repository

This repository is **not** a framework, and it is **not** a wrapper around an LLM API. It is a systems-engineering lab built to answer one question properly:

> **How do you build reliable, auditable, production-grade software on top of a component that is fundamentally probabilistic?**

Every folder here is a self-contained, minimal, runnable proof-of-concept for one architectural concern in agentic AI systems — state control, crash recovery, retries, parallel execution, model routing, edge inference, retrieval, memory, multi-agent orchestration, security, and observability. The code is intentionally small (30–100 lines per concept). The goal is **transferable mental models**, not framework mastery — you should be able to look at any agent framework (LangGraph, Temporal, AutoGen, CrewAI, Restate...) afterward and immediately recognize which of these primitives it is (re)implementing, and what trade-off it made.

This is a personal engineering-education project, structured as a progressive curriculum with runnable reference code at each stop.

---

## 🎯 Core Philosophy

The entire lab is built on a single axiom, referred to throughout as **AI Systems Thinking**:

> **LLMs are probabilistic. Software must be deterministic.**
> Your job as the architect is not to make the model more predictable — it's to build a deterministic runtime *around* an inherently unpredictable component, so the unpredictability is contained, observable, and recoverable.

Left uncontrolled, an LLM-driven agent will:
- Skip steps and hallucinate progress it hasn't actually made
- Get stuck in infinite tool-calling loops
- Lose all state and context the moment a process crashes or the network drops
- Silently return `200 OK` while reasoning has completely derailed

Every phase in this repository exists to close one of these failure modes.

### The four architectural layers

```
                    ┌──────────────────────┐
                    │  AI-NATIVE PRODUCT   │
                    │  & SYSTEM ARCHITECT  │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                  │
       GENERATIVE UX                       AI SECURITY
              │                                  │
              └────────────────┬────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │    MODEL ROUTING     │
                    │    EDGE INFERENCE    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │    AGENT RUNTIME     │
                    │    WORKFLOW ENGINE   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ RELIABILITY & STATE  │
                    │ FSM / DURABILITY     │
                    └──────────────────────┘
```

Reliability and state control are the foundation. Nothing above them can be trusted if the base isn't crash-proof and auditable.

---

## 🏗️ System Architecture

The one principle that repeats at every layer of this lab:

> **The LLM never touches the outside world directly.** It only ever *proposes* an intent (a structured, validated suggestion). A deterministic runtime — guarded by an FSM, a tool contract, and a durability layer — is the only thing with permission to actually execute anything.

```
       ┌────────────────────────────────────────────────────────┐
       │                   DETERMINISTIC RUNTIME                │
       │                                                        │
       │   ┌──────────────┐     FSM Guard Check     ┌───────┐   │
       │   │              │ ──────────────────────► │       │   │
       │   │ Context &    │                         │ LLM   │   │
       │   │ State Store  │ ◄────────────────────── │ Engine│   │
       │   └──────────────┘    Structured JSON      └───────┘   │
       │          ▲                                     │       │
       │          │          Durable Activity           │       │
       │          └─────────────────────────────────────┘       │
       │                        Tool Result                     │
       └────────────────────────────────────────────────────────┘
```

This "runtime sandwich" — **FSM guard → validated intent → durable, idempotent execution → checkpoint → observe** — is the pattern every subsequent phase (routing, RAG, memory, multi-agent, security) plugs into.

---

## 🗺️ The 14 Phases

Each phase closes exactly one architectural gap opened by the previous one. They are designed to be read **in order** the first time through.

| # | Phase | Core Question It Answers | Key Concepts |
|---|-------|---------------------------|---------------|
| **1** | [AI Systems Thinking](#phase-1--ai-systems-thinking) | Why do agents go rogue in the first place? | Probabilistic vs. Deterministic |
| **2** | [FSM & State](#phase-2--fsm--state) | How do we stop an agent from skipping or reordering steps? | States, Events, Transitions, Guards, Invariants |
| **3** | [Durable Execution](#phase-3--durable-execution) | How does an agent survive a mid-task crash without redoing (and re-paying for) work? | Workflow vs. Activity, Memoization, Replay |
| **4** | [Failure, Retry & Idempotency](#phase-4--failure-retry--idempotency) | How do we retry safely without duplicating side effects or DDoS-ing our own dependencies? | Backoff + Jitter, Idempotency Keys |
| **5** | [DAG & Workflow Execution](#phase-5--dag--workflow-execution) | How do independent sub-tasks run in parallel instead of burning latency serially? | Fan-out/Fan-in, Immutable Message Passing |
| **6** | [Agent Runtime](#phase-6--agent-runtime) | How do we finally let the LLM make decisions — safely? | Context Manager, Intent Validator, Tool Dispatcher |
| **7** | [Observability & Evals (v1)](#phase-7--observability--evals-v1) | How do we know *why* an agent behaved a certain way, not just *that* it returned 200? | Tracing, Deterministic vs. LLM-as-Judge Evals |
| **8** | [Model Routing](#phase-8--model-routing) | Why pay GPT-4o/Sonnet prices for a task a small model can handle? | Static / Semantic / Cascading Routing, Fallback |
| **9** | [Inference & Edge AI](#phase-9--inference--edge-ai) | How do we run models under a strict RAM/latency budget on real hardware? | Quantization, KV Cache, Memory-Bound Inference |
| **10** | [RAG & Context Management](#phase-10--rag--context-management) | How do we inject external knowledge without drowning the model in noise? | Chunking, Hybrid Search, Re-ranking, RRF |
| **11** | [Memory Systems](#phase-11--memory-systems) | How does an agent remember users and its own past across sessions? | STM/LTM, Semantic vs. Episodic Memory, Consolidation |
| **12** | [Multi-Agent Orchestration & Swarms](#phase-12--multi-agent-orchestration--swarms) | How do specialized agents collaborate without descending into chaos? | Supervisor vs. Peer-to-Peer, Handoff Contracts |
| **13** | [Security, Sandboxing & Safety](#phase-13--security-sandboxing--safety) | How do we stop an agent from becoming a "confused deputy"? | Prompt Injection, Dual-LLM Pattern, AST Sandboxing |
| **14** | [Observability, Tracing & Evaluation (v2)](#phase-14--observability-tracing--evaluation-v2) | How do we monitor a fully-assembled, secured, multi-agent system in production? | OTel Semantic Conventions, Golden Datasets, CI/CD Regression |

> Phases **15–17** (*Generative UX, Distributed AI Systems, Final Architecture Integration*) are part of the broader learning roadmap and are tracked in [Roadmap & Progress](#-roadmap--progress) — implementation folders for these will land in this repository as they are completed.

---

<details>
<summary><h3>Phase 1 — AI Systems Thinking</h3></summary>

Not a folder of code — a worldview. The foundational claim: an LLM is a probabilistic next-token predictor; real software needs deterministic guarantees. Every other phase is a concrete implementation of "wrap the probabilistic core in a deterministic shell." This lens gets revisited at Observability and Security, where new dimensions of the same principle show up.

</details>

<details>
<summary><h3>Phase 2 — FSM & State</h3></summary>

**📁 `fsm/`**

A Finite State Machine acts as a strict commander standing over the LLM: the system exists in exactly one state at a time, and can only move to the next one when a *permitted* event occurs.

| Element | Definition | Example |
|---|---|---|
| **State** | The system's current ground truth | `READING` |
| **Event** | A signal that something happened | `FILE_FOUND` |
| **Transition** | The rule for moving between states | `READING --FILE_FOUND--> ANALYZING` |
| **Invariant** | A rule that must never break, under any circumstance | "No moving to REPORT until file is read" |

Two control layers make the FSM more than a lookup table:
- **Guard** — a boolean condition checked *before* a transition executes (e.g., reject `ANALYZING` if the file read `0` bytes)
- **Invariant** — a hard rule enforced for the entire lifecycle (e.g., "total retries across all states ≤ 3")

An out-of-order event (e.g., `REPORT_GENERATED` arriving while in `READING`) is **rejected** with an exception — the FSM never allows shortcuts or invalid data to slip into the next state.

**Persistence is bolted directly onto the FSM**: every transition is checkpointed to disk *synchronously, before* the next step executes. On reboot, the FSM reads its last known state from disk and resumes exactly where it left off — no wasted re-work, no lost context.

```python
def transition_to(self, new_state: State, guard: bool = True) -> None:
    if new_state not in self.TRANSITIONS[self.state]:
        raise ValueError(f"Illegal transition: {self.state} -> {new_state}")
    if not guard:
        raise PermissionError(f"Guard failed for target state: {new_state}")
    self.state = new_state
    self._checkpoint()  # disk is updated before in-memory state is trusted
```

**Failure semantics at the FSM level:** on error, the system routes to one of three outcomes: `Retry` (transient), `Fail` (deterministic/permanent), or `Escalate` (human-in-the-loop) — the taxonomy fully explored in Phase 4.

</details>

<details>
<summary><h3>Phase 3 — Durable Execution</h3></summary>

**📁 `durable_execution/`**

The problem: a multi-step pipeline (extract → summarize via LLM → save to DB) crashes mid-flight due to a network blip. On restart, a naive re-run calls the LLM *again* — burning tokens, time, and (because LLMs are non-deterministic) potentially getting a **different answer** the second time.

**Durable Execution** (the pattern behind Temporal, Restate) gives your workflow function memory that survives a crash:

> **Golden rule:** on replay, steps that already succeeded are never re-executed — their previous result is loaded from disk and injected back in (Memoization / Replay).

The architecture splits into two strictly separated roles:

- **Workflow (orchestrator)** — must be **100% deterministic**. No `time.now()`, no `random()`, no direct HTTP calls. Just sequencing logic.
- **Activity (executor)** — the only place allowed to touch the outside world (LLM calls, disk I/O, DB writes). Each Activity is independently retried and cached.

```python
def run_activity(step_id: str, func, *args):
    log = json.loads(LOG_FILE.read_text()) if LOG_FILE.exists() else {}
    if step_id in log:
        return log[step_id]              # REPLAY — skip real execution
    result = func(*args)                 # EXECUTE — real, first-time run
    log[step_id] = result
    LOG_FILE.write_text(json.dumps(log, indent=2))
    return result
```

**Why the Workflow/Activity split is non-negotiable:** if you put `datetime.now()` or `random()` directly inside the Workflow body, the decision path diverges on every replay, and the orchestration engine can no longer line up in-flight variables with the events it already logged to disk. That's a silent, hard-to-debug **non-deterministic replay bug** — one of the most common mistakes when building this pattern from scratch.

</details>

<details>
<summary><h3>Phase 4 — Failure, Retry & Idempotency</h3></summary>

**📁 `Failure-Retry-Idempotency/`**

Not all failures are equal. Treating them identically is the first mistake most engineers make:

| Failure Type | Nature | Example | Strategy |
|---|---|---|---|
| **Transient** | Temporary, non-deterministic | `503`, `429 Rate Limit` | Retry with backoff |
| **Permanent** | Deterministic, will never succeed | `401 Auth Failure`, validation error | Fail fast — no retry |
| **Poison Pill** | Input itself causes repeated crashes | Malformed JSON, overflow | Quarantine / escalate |

**Exponential Backoff + Jitter** prevents the *Thundering Herd Problem* — if 10 agents all hit a `429` and all retry after exactly 1 second, they synchronize and take the downstream service down together. Backoff staggers the wait time exponentially (`1s → 2s → 4s → 8s`); jitter randomizes it further so agents desynchronize.

**Idempotency** is the other half of safe retries:

> An operation is idempotent if running it N times produces exactly the same effect as running it once.

Without this, a retried "send email" or "process payment" call can double-fire a side effect that already succeeded — the request went through, but the response was lost to a network drop, triggering a needless retry. The fix is an **Idempotency Key** (e.g., `hash(task_id + step_id)`) attached to every request; if the receiving layer has already processed that key, it returns the cached result instead of re-executing.

```python
sleep_time = random.uniform(0, min(8.0, base_delay * (2 ** attempt)))  # Full Jitter
```

**Closing the deterministic foundation:** Phases 1–4 together produce a *crash-proof runtime* — any LLM can now be mounted on top of it without fear of network drops, financial waste from duplicate side effects, or anarchic step-skipping.

</details>

<details>
<summary><h3>Phase 5 — DAG & Workflow Execution</h3></summary>

**📁 `dag/`**

If FSM is the "compass and lifecycle supervisor," DAG is the "roadmap and parallel-execution engine." A single FSM state (e.g., `EXECUTE`) often hides multiple independent sub-tasks — fetching 5 documents, merging results, running validation code. Running them serially tanks latency; FSM alone has no concept of "run these things concurrently."

A **Directed Acyclic Graph** is built from:
- **Nodes** — executable Activities (API calls, DB queries, text processing)
- **Edges** — data or ordering dependencies between nodes

If `Task_A` and `Task_B` share no dependency, they run fully in **parallel**. `Task_C`, dependent on both, waits for a **fan-in join**. "Acyclic" means no path may loop back to the start node — that would deadlock.

> **Architectural principle:** each node is a **pure function** — read-only input, new output. The DAG engine (not shared mutable state) is responsible for injecting each node's output into the next node's input. Sharing a mutable dict across parallel branches is the single most common way to introduce race conditions here.

**Failure modes specific to DAGs:**
- **Branch isolation** — if one of 3 parallel branches fails, do you `short-circuit` (cancel the whole DAG — for tightly coupled work) or go `best-effort` (push forward with partial data — fine for something like LLM summarization that tolerates 80% coverage)?
- **Static vs. Dynamic DAG** — a static graph is fully known before execution (`Fetch → Process → Save`). A **Dynamic/Agentic DAG**, where the LLM itself decides what nodes to add mid-run, is far harder to manage because the LLM can accidentally introduce a cycle — requiring a runtime guard that detects and rejects cycles on the fly.

```python
ready_nodes = [
    node for name, node in self.nodes.items()
    if name not in completed and node.dependencies.issubset(completed)
]
tasks = [self._run_node(node, results) for node in ready_nodes]
node_results = await asyncio.gather(*tasks)   # true fan-out
```

</details>

<details>
<summary><h3>Phase 6 — Agent Runtime</h3></summary>

**📁 `agent-runtime/`**

With all deterministic layers in place (FSM, Durable Execution, Retry/Idempotency, DAG), Phase 6 is the first time the LLM is mounted as a **decision-maker** on top of this chassis.

An Agent Runtime is the control loop implementing **Observe → Think → Act → Verify** (the ReAct pattern), built from four modules:

- **Context Manager** — assembles system prompt, tool-call history, and current FSM state for the LLM
- **Intent Parser & Validator** — takes the LLM's probabilistic output and forces it through a Pydantic schema
- **FSM Guardrail** — checks whether the LLM's requested action is even legal in the current FSM state
- **Tool Dispatcher** — executes the approved action as a Durable Activity (retryable, idempotent, cacheable)

> **Non-negotiable principle:** the LLM never calls a tool or mutates a database directly. It only ever *proposes* an intent. The Runtime evaluates, logs, and then executes that proposal inside a durable substrate.

The critical failure modes this phase guards against include the **Death Spiral** (an agent stuck endlessly re-calling the same tool) and **Unbounded Autonomy** — both closed off by the combination of FSM guard checks and a hard cap enforced by the Tool Dispatcher.

</details>

<details>
<summary><h3>Phase 7 — Observability & Evals (v1)</h3></summary>

**📁 `Observability-Eval-Engine/`**

Traditional APM (Datadog, Prometheus-style monitoring centered on HTTP status codes, CPU, latency) fails for agentic systems because failures here are **silent**: an API can return `200 OK`, throw zero exceptions, and still have completely hallucinated its answer or burned 3x the expected tokens.

> **Principle:** in AI systems, we don't log code — we trace the *reasoning path* (graph of thought) and *state transitions*.

Two complementary concepts:

| Concept | What It Is |
|---|---|
| **Observability (Tracing)** | Live production monitoring — a `Trace` is the full run; a `Span` is each sub-operation (an LLM call, a tool call) |
| **Evaluations (Evals)** | The replacement for unit tests on non-deterministic behavior — did the output stay correct, faithful, and on-prompt? |

A **two-tier eval engine**:
- **Deterministic Evals** (fast, cheap) — schema validation, latency thresholds, forbidden-word checks
- **Probabilistic Evals / LLM-as-a-Judge** — a separate model scores **Faithfulness** (is the answer grounded in the input data, or invented?) and **Answer Relevance**

**Operational risks to design around:**
- **PII & data leakage in traces** — shipping raw user data/API keys to an external logging system without a redaction layer
- **Goodhart's Law in LLM-as-a-Judge** — optimizing purely for judge-score inflates polish over substance
- **Telemetry overhead** — logging full multi-KB prompts on every call adds real latency and storage cost

</details>

<details>
<summary><h3>Phase 8 — Model Routing</h3></summary>

**📁 `model-routing/`**

Sending every request — from trivial classification to five-step reasoning — to a heavyweight model (GPT-4o, Claude Sonnet) is a costly, latency-inducing anti-pattern. A **Model Router** is a cheap, sub-20ms decision layer sitting in front of the main LLM call, dispatching by complexity, schema needs, latency SLA, and cost budget.

```
                      MODEL ROUTER
 User Request ──► 1. Heuristic Check (Regex/Length)
                  2. Semantic Embedding Distance
                  3. SLA & Cost Policy Evaluation
                       │
     ┌─────────────────┼─────────────────┐
     ▼ (Low)            ▼ (Medium)          ▼ (High Reasoning)
 Local SLM         Fast Cloud            Heavy LLM
 (Llama 8B)        (Flash / Haiku)       (Sonnet / GPT-4o)
```

Three routing strategies, cheapest to most sophisticated:
1. **Static / Rule-Based** — prompt length, keywords, requested tool type → near-zero latency
2. **Semantic Routing** — embed the prompt, compare cosine distance against known intent clusters → ~10–30ms
3. **Model-Based Cascading** — a tiny model scores complexity `0.0–1.0`; below `0.3` → cheap tier, above `0.7` → heavy tier

**Fallback cascading** is just as important as the initial routing decision: on `429`, `503`, or a schema-format violation from the primary model, the router transparently escalates to a fallback tier — without ever halting the FSM.

**Risks unique to routing:**
- **Router latency tax** — if the router itself takes 200ms to save you from a 1s call, you've erased the value
- **Small-model schema fragility** — SLMs are meaningfully worse at producing valid complex JSON; routing complex structured-output tasks to them spikes validation failures
- **Routing flapping** — trivial prompt variations shouldn't cause wildly inconsistent model-tier selection, which shows up to users as inconsistent quality

</details>

<details>
<summary><h3>Phase 9 — Inference & Edge AI</h3></summary>

**📁 `Inference-KV-Cache/`**

The central hardware bottleneck: token generation is **memory-bandwidth-bound, not compute-bound**. Every token requires streaming the *entire* model's weights from RAM into cache/VRAM.

> **Concrete result:** an 8B model at FP16 (16 GB) running on hardware with 40 GB/s memory bandwidth has a theoretical ceiling of `40 / 16 = 2.5 tokens/sec` — regardless of core count.

**Quantization** trades precision for bandwidth headroom:

| Precision | 8B Model Size | Perplexity Loss | Best For |
|---|---|---|---|
| FP16 | ~16 GB | 0% (baseline) | Cloud servers |
| Q8_0 | ~8.5 GB | Negligible (<1%) | High-fidelity local |
| **Q4_K_M** | **~4.5 GB** | **Minor (1–3%)** | **Sweet spot for Edge** |
| Q2_K | ~2.8 GB | Severe (>15%) | Unusable for reasoning |

`Q4_K_M` is the go-to for edge deployment: ~75% size reduction with minimal reasoning collapse.

**KV Cache** stores attention Key/Value outputs so the model doesn't recompute the full attention matrix at every step — but this cache itself grows RAM usage linearly with context length (an 8B model at 8k context, FP16 KV, can eat 1.5–2 GB on its own). Mitigations: quantized KV cache (INT8/INT4) and paged-attention-style memory management.

**Failure modes unique to edge/mobile (e.g. Termux on Android):**
- **OOM Killer** — Android silently `SIGKILL`s the process on RAM exhaustion, no graceful error
- **Thermal throttling** — sustained CPU inference can cut clock speed up to 50%, linearly increasing latency
- **Context degradation in low-bit models** — 4-bit quantized models degrade into repetition loops faster than full-precision ones as context grows past ~4k tokens

The reference engine here is a **memory-budget calculator** that computes weight size + KV cache size + runtime overhead against available RAM, and returns a hard `feasible: true/false` verdict *before* you try to load the model — turning a runtime OOM crash into a design-time check.

</details>

<details>
<summary><h3>Phase 10 — RAG & Context Management</h3></summary>

**📁 `RAG-Context-Management/`**

Naive RAG (fixed-size chunking + a single vector store) reliably fails in production for three reasons: **low precision** (retrieved noise), **low recall** (misses exact keywords/IDs), and **"lost in the middle"** (LLMs pay less attention to the middle of a long context).

> **Architectural principle:** the retrieval layer isn't a vector store — it's a three-stage pipeline: **Chunking → Hybrid Retrieval → Re-ranking**.

```
Raw Docs → [Semantic/AST-aware Chunking] → [Hybrid Search: Dense + Sparse]
         → [Reciprocal Rank Fusion] → [Cross-Encoder Re-rank] → Pure Context to LLM
```

- **Chunking** — AST/code-aware (never split a function mid-body) or semantic (chunk boundary set where embedding distance between consecutive sentences crosses a threshold)
- **Hybrid Search** — Dense (vector embeddings) is great at abstract similarity but weak on exact identifiers; Sparse (BM25/TF-IDF) nails exact keyword matches but has no semantic understanding. Combined via **Reciprocal Rank Fusion (RRF)**:  
  `RRF_score(d) = Σ 1 / (k + rank_m(d))`, typically `k = 60`.
- **Re-ranking** — a slower but far more precise **Cross-Encoder** (e.g., BGE-Reranker) filters the top-K candidates down to the 5 most relevant, cutting context noise by up to ~70%.

**Failure modes:**
- **Chunk boundary shattering** — a key definition split across two chunks loses its meaning; the fix is a **Parent-Document Retriever** (search on small chunks, inject the larger parent chunk into context)
- **Context pollution** — irrelevant chunks confuse the model into hallucinating
- **Retrieval latency explosion** — vector search + BM25 + re-ranking must run async/parallel or latency stacks up

</details>

<details>
<summary><h3>Phase 11 — Memory Systems</h3></summary>

**📁 `Memory-Systems/`**

Keeping the entire conversation history in the context window doesn't scale — token limits, latency, and cost all break down. Memory architecture maps loosely onto human cognitive memory, split into four layers:

```
                 AGENT MEMORY SYSTEM
       ┌───────────────┼───────────────┐
       ▼                ▼                ▼
 Short-Term        Semantic LTM      Episodic LTM
 (Working)          (Fact/KV)        (Experience)
 Sliding Buffer    User Profiles    Execution Logs
                   & Domain Facts   & Self-Correction
```

1. **Working / Short-Term Memory** — the live session context, managed via sliding window + dynamic summarization
2. **Semantic Long-Term Memory** — stable facts and preferences ("user's preferred language is Python"), stored as KV/knowledge-graph/document store
3. **Episodic Long-Term Memory** — a history of past actions and outcomes ("on Feb 2nd, connecting on port 5432 timed out; 5433 fixed it"), retrieved by similarity + timestamp
4. **Procedural Memory** — the agent's static instructions, system prompts, and FSM structure

**Memory Consolidation** — the process of promoting STM into LTM — runs as an **async background worker**, decoupled from the user-facing response loop so it never adds latency to the interactive path. Not everything earns a place in LTM: each candidate fact is scored on **Recency**, **Importance** (judged by a small model), and **Frequency** of recall.

**Conflict resolution** — if the user previously said "I'm in Tehran" and later says "I moved to Berlin," the system needs **Temporal Versioning** (`created_at` / `valid_until` per fact) and **Upsert-via-Entity-Extraction** logic: query the store by entity before writing, and overwrite/deprecate the prior value.

**Failure modes:**
- **Memory poisoning** — a hallucinated fact that gets written to LTM gets reinforced and repeated in every future turn
- **Stale context overhead** — over-injecting old memories causes context distraction and degrades reasoning quality
- **Async race conditions** — two rapid user messages can race the consolidation worker and corrupt memory state

</details>

<details>
<summary><h3>Phase 12 — Multi-Agent Orchestration & Swarms</h3></summary>

**📁 `Multi-Agent-Router-Handoff-Engine/`**

A single monolithic agent trying to plan, code, execute, test, and fix simultaneously runs into **Prompt Entropy** — as tool count and instruction count grow, tool-hallucination rate rises non-linearly, and unrelated execution history (e.g., a 1000-line debugger dump) pollutes the reasoning space needed for high-level planning.

> **Architectural fix:** decompose into a network of single-responsibility agents with strict context isolation and restricted toolsets.

Two dominant topologies:

```
[Hierarchical / Supervisor]              [Peer-to-Peer / Handoff Swarm]
        Supervisor                              Agent A
       ┌────┴────┐                                 │ (handoff)
   Worker A   Worker B                          Agent B
```

- **Hierarchical / Supervisor** — a top-level agent decomposes the problem, delegates to workers, merges results. Highly predictable, testable, DAG-shaped. Best for: linear code-gen pipelines, ETL, document processing.
- **Peer-to-Peer Swarm / Handoff** — no supervisor; each agent calls `transfer_to_agent(...)` directly when done. Far more adaptive to unforeseen error paths. Best for: complex customer support, autonomous R&D loops.

**Critical failure modes:**
- **Ping-pong / endless handoff loop** — Agent A hands to B, B lacks info and bounces it back to A, repeat until budget exhausted. Mitigated with a hard **global handoff budget** and O(V+E) cycle detection on the handoff graph.
- **State leakage & context bloat** — passing full conversation history on every handoff defeats the point of isolation. Fix: **explicit, small Pydantic payload contracts** between agents, not full history transfer.
- **Cascade failure** — an error in the first agent's output (e.g., a bad plan) gets accepted as ground truth by the next agent, propagating the mistake downstream.

```python
if current_agent_name in handoff_history[-2:]:
    raise RuntimeError(f"[SWARM CRASH] Ping-pong loop detected on '{current_agent_name}'!")
```

</details>

<details>
<summary><h3>Phase 13 — Security, Sandboxing & Safety</h3></summary>

**📁 `Security-Sandboxing-Safety/`**

In classic software, the code defines what's allowed. In agentic systems, the LLM is a **stochastic interpreter** that can reinterpret instructions based on whatever untrusted input lands in its context — turning a well-scoped agent into a **Confused Deputy**: it retains its legitimate credentials, but gets tricked into using them on an attacker's behalf.

```
              UNTRUSTED INPUT (User Prompt / RAG / Web Result)
                          │
                Agent LLM (Context Injection)
                          │
              [Confused Deputy Vulnerability]
     ┌─────────────────────┼─────────────────────┐
Direct/Indirect      Unauthorized             Dynamic Code
Prompt Injection     Tool Calling             Execution
```

- **Direct injection (jailbreak)** — user tries to talk the model out of its guardrails
- **Indirect injection (far more dangerous)** — malicious instructions embedded in *retrieved* content (a poisoned PDF in your RAG pipeline, scraped webpage text) that the agent treats as legitimate

**Defense-in-depth**, four layers deep:

```
Layer 1: Input Sanitization & Pre-execution Policy Check
Layer 2: Privilege Separation (Dual-LLM Pattern)
Layer 3: AST / Static Code Analysis (before runtime execution)
Layer 4: Infrastructure Isolation (gVisor / MicroVM Sandbox)
```

- **Dual-LLM Pattern** — an *Unprivileged LLM* processes/summarizes raw untrusted content (no tool access at all); a separate *Privileged LLM* decides on tool execution based only on the filtered, structured output of the first
- **Least Privilege for tools** — granular, narrowly-scoped tools (`git_clone`, `read_file`) instead of a general `execute_bash`; destructive operations (DB deletes, payments, mass email) require explicit Human-in-the-Loop approval

**Sandbox comparison for LLM-generated code execution:**

| Sandbox | Isolation | Startup Latency | Kernel-Escape Resistance |
|---|---|---|---|
| `exec()` / `eval()` | None | 0ms | None — full RCE risk |
| Docker (standard) | Medium | ~100–500ms | Weak — shares host kernel |
| **gVisor / Firecracker** | **Very high** | **~5–20ms** | **Very high — virtual kernel** |
| WebAssembly (WASM) | High | <1ms | High — bound to memory sandbox |

Industry standard: **gVisor or Firecracker MicroVMs**, with `--network none` for full network isolation on any untrusted code path.

The reference implementation is a **static AST guard** that walks the Python AST of LLM-generated code *before* it ever reaches a sandbox, rejecting forbidden imports (`os`, `subprocess`) and forbidden calls (`eval`, `exec`, `open`, `__import__`, `compile`) outright.

```python
def visit_Call(self, node: ast.Call):
    if isinstance(node.func, ast.Name):
        if node.func.id in {"eval", "exec", "open", "__import__", "compile"}:
            self.violations.append(f"Forbidden function call: '{node.func.id}()'")
```

</details>

<details>
<summary><h3>Phase 14 — Observability, Tracing & Evaluation (v2)</h3></summary>

**📁 `Observability-Tracing-Evaluation/`**

The capstone monitoring layer, applied to the *fully assembled* system — secured, multi-agent, memory-backed. Traditional APM metrics (CPU, HTTP status, latency) are structurally blind to agent-specific failures: a request can return `200 OK` while the agent looped through 5 wrong tools, burned $5 in tokens, and produced a fully hallucinated answer.

```
             USER AGENT REQUEST
                     │
        Execution Graph / DAG
     (Spans: Thought → Tool → Memory)
                     │
   ┌─────────────────┼─────────────────┐
Tracing         Cost & Token        Evaluations
(Trajectory)     Attribution        (LLM-Judge)
```

Monitoring rests on three pillars: **Trajectory Tracing** (every decision-tree step logged as a span), **Token & Cost Attribution** (exact cost breakdown by model/tool/user), and **Behavioral Evals** (reasoning quality + drift detection).

Standardized on **OpenTelemetry Semantic Conventions for GenAI** — every agent run is one `Trace`, decomposed into typed `Spans`:

| Span Kind | Key Attributes |
|---|---|
| Agent / Workflow | `trace_id`, `total_cost`, `total_tokens`, `status` |
| LLM Inference | `model_name`, `prompt_tokens`, `completion_tokens`, `temperature` |
| Tool Execution | `tool_name`, `input_args`, `output_result`, `latency_ms`, `error` |
| Memory Access | `retrieval_query`, `top_k`, `vector_scores`, `latency_ms` |

**Evaluation matrix**, run both offline (CI/CD) and online (production guardrails):
- **Trajectory Efficiency** — ratio of optimal step count to actual step count; a low score signals the agent got confused choosing tools
- **Tool Selection Accuracy** — did it call the right tool with schema-valid inputs?
- **Faithfulness** — is the final answer fully grounded in tool/RAG output, or partly invented?
- **Goal Completion Rate** — judged via LLM-as-a-Judge against the user's original ask

**CI/CD regression pattern:** maintain a set of ≥50 **Golden Test Cases** (input scenario + expected trajectory + reference output); run them automatically in staging before merge; **fail the build** if Goal Completion or Tool Accuracy drops by more than 2%. This is what catches the silent damage a one-word system-prompt edit or a model upgrade can do to tool-selection behavior.

</details>

---

## 📂 Repository Map

```text
ai-runtime-lab/
│
├── fsm/                                    # Phase 2  — FSM & State
├── durable_execution/                      # Phase 3  — Durable Execution
├── Failure-Retry-Idempotency/              # Phase 4  — Failure, Retry & Idempotency
├── dag/                                    # Phase 5  — DAG & Workflow Execution
├── agent-runtime/                          # Phase 6  — Agent Runtime
├── Observability-Eval-Engine/              # Phase 7  — Observability & Evals (v1)
├── model-routing/                          # Phase 8  — Model Routing
├── Inference-KV-Cache/                     # Phase 9  — Inference & Edge AI
├── RAG-Context-Management/                 # Phase 10 — RAG & Context Management
├── Memory-Systems/                         # Phase 11 — Memory Systems
├── Multi-Agent-Router-Handoff-Engine/      # Phase 12 — Multi-Agent Orchestration & Swarms
├── Security-Sandboxing-Safety/             # Phase 13 — Security, Sandboxing & Safety
├── Observability-Tracing-Evaluation/       # Phase 14 — Observability, Tracing & Evaluation (v2)
│
├── .venv/
├── .gitignore
└── README.md
```

> Phase 1 (*AI Systems Thinking*) is conceptual by design and has no dedicated folder — it's the lens every other folder is built through.

---

## 🚀 Getting Started

Each folder is a **standalone proof-of-concept** — no shared dependencies between phases beyond the Python standard library (plus `asyncio` for the DAG engine). Pick any phase and run its script directly:

```bash
git clone https://github.com/Ali-hey-0/ai-runtime-lab.git
cd ai-runtime-lab

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

cd fsm/
python <script_name>.py
```

Every script includes a `if __name__ == "__main__":` block that runs a self-contained test scenario — crash simulation for `fsm/`, replay verification for `durable_execution/`, parallel fan-out for `dag/`, and so on. Read the code, run it, break it on purpose, then move to the next phase.

---

## 🧭 How to Use This Repository

This isn't meant to be read start-to-finish in one sitting. A useful way to prioritize, based on transferability across future projects:

**🔴 Learn deeply — highest architectural leverage**
State Machines · Durable Execution · Failure Semantics · DAG/Workflow · Agent Runtime · Model Routing · Agentic Security

**🟠 Understand well — you should be able to design and evaluate trade-offs here, not necessarily hand-roll a runtime from scratch**
Observability · Agent Evals · LLM Inference · Quantization · Structured Generation · Distributed Systems

**🟡 Architectural literacy is enough**
Specific runtimes (GGUF internals, ONNX Runtime specifics, WebGPU, RKNN), Dynamic UI frameworks — know what's *possible* and what the trade-offs are, without memorizing every API surface.

---

## 🛣️ Roadmap & Progress

- [x] Phase 1 — AI Systems Thinking
- [x] Phase 2 — FSM & State
- [x] Phase 3 — Durable Execution
- [x] Phase 4 — Failure, Retry & Idempotency
- [x] Phase 5 — DAG & Workflow Execution
- [x] Phase 6 — Agent Runtime
- [x] Phase 7 — Observability & Evals (v1)
- [x] Phase 8 — Model Routing
- [x] Phase 9 — Inference & Edge AI
- [x] Phase 10 — RAG & Context Management
- [x] Phase 11 — Memory Systems
- [x] Phase 12 — Multi-Agent Orchestration & Swarms
- [x] Phase 13 — Security, Sandboxing & Safety
- [x] Phase 14 — Observability, Tracing & Evaluation (v2)
- [ ] Phase 15 — Generative UX / Dynamic UI *(schema-driven & intent-driven UI)*
- [ ] Phase 16 — Distributed AI Systems *(distributed state, queues, failover, backpressure)*
- [ ] Phase 17 — Final Architecture Integration *(unify all 16 phases into one coherent system)*

A Persian-language (فارسی) version of this README/curriculum is planned as a future addition.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built as a systems-thinking exercise, not a framework.**
If it saves you from wrapping an LLM in a `while True:` loop and calling it an agent — it did its job.

</div>
