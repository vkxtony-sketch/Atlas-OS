# Atlas OS

An experimental, **local-first**, open-source multi-agent operating
architecture. Atlas coordinates multiple specialised agents and tools
behind a unified Execution layer so the user describes a goal and
Atlas figures out *how* to accomplish it.

> **Status — early experimental.** This build is honest about what it
> does and doesn't do. The "Fully implemented" column in [the feature
> map](#feature-map-real-vs-not) below is precise, not marketing.

---

## Quick start

```bash
# 1. Install (Python 3.10+)
pip install -r requirements.txt

# 2. Run the CLI
./scripts/run_cli.sh "design a recipe website"

# 3. Run the API (FastAPI)
./scripts/run_api.sh
# → POST {"goal": "..."} -> http://127.0.0.1:8000/run
# → GET  http://127.0.0.1:8000/agents | /teams | /audit | /history

# 4. Run the dashboard (Streamlit)
./scripts/run_ui.sh

# 5. Run the test suite
./scripts/run_tests.sh
```

Or with raw Python:

```bash
python main.py "design a recipe website"
```

The result is always a 6-key contract dict:

```python
{
  "planner":   {...},      # planning output
  "research":  {...} | None,
  "coding":    {...} | None,
  "critic":    {"score": int, "verdict": "pass"|"fail", "issues": [...]},
  "consensus": {"consensus_result": ..., "confidence": float, "total_votes": int},
  "status":    "complete" | "needs_revision" | "empty"
}
```

---

## Configuration

Everything is env-driven and lives in `core.config.AtlasSettings`. See
[`.env.example`](.env.example) for every knob.

The most important flags:

| var | default | meaning |
|---|---|---|
| `ATLAS_LLM_PROVIDER` | `mock` | one of `mock` `template` `http` `echo` |
| `ATLAS_LLM_HTTP_URL` | empty | OpenAI-compatible endpoint for `http` provider |
| `ATLAS_AUTO_DENY` | `false` | deny every side-effect action |
| `ATLAS_AUTO_APPROVE` | `false` | dev convenience: grant every action |
| `ATLAS_ALLOW_<UPPER>` | `false` | selectively grant `git.commit` etc. |
| `ATLAS_ALLOW_CODE_EXECUTION` | `false` | must remain off until a real sandbox exists |
| `ATLAS_AUDIT_LOG_PATH` | `atlas_audit.log` | append-only JSONL audit trail |
| `ATLAS_ENABLE_ENCRYPTED_MEMORY` | `false` | opt-in AES-GCM for memory at rest |

---

## Architecture

```
                ┌─────────────────────────────────────────────┐
                │              MultiAgentExecutive             │
                │  • decomposes goals into tasks              │
                │  • invokes planner / researcher / coder      │
                │  • loops with critic feedback until target  │
                │  • merges with ConsensusEngine               │
                └─────────────────────────────────────────────┘
                                  │
       ┌───────────────┬───────────┼─────────────┬─────────────┐
       ▼               ▼           ▼             ▼             ▼
   PlannerAgent   ResearchAgent  CoderAgent   CriticAgent   Teams(8)
                                                          │
                              ┌─────────────────────────────┘
                              ▼
        ┌──────────────────────────────────────────────────────────┐
        │  Teams: architecture · backend · frontend · security     │
        │         performance · documentation · testing · research │
        │  Agents (15+): planner, coder, critic, researcher,      │
        │              code_reviewer, security_reviewer,           │
        │              performance_reviewer, documentation_writer, │
        │              qa_engineer, knowledge, memory, git,         │
        │              deployment, terminal, file                  │
        └──────────────────────────────────────────────────────────┘

   LLM facade  ─▶ core/llm_providers/{mock,template,http,echo}
   Memory      ─▶ core/memory/{store,shared_store} [+ optional AES-GCM]
   Knowledge   ─▶ core/knowledge/{indexer,search}     (offline TF-IDF)
   Tools       ─▶ core/tools/{router,web_tool,python_tool ← stub-only}
   Permissions ─▶ core/permissions/gate.py            (deny by default)
   Audit       ─▶ core/audit/log.py                   (append-only)
   Plugins     ─▶ core/plugins/{manager,manifest}     (subprocess policy)
   Integrations▶ core/integrations/{runner,connectors/{git_cli,github,
                                 docker,vscode,notion,obsidian}}
   Hardware    ─▶ core/system/detect.py               (CPU/RAM/OS/GPU)
```

---

## Feature map (real vs. not)

The columns below describe *this build*, not the future. Where the
spec item isn't implementable in this build we mark it clearly so the
feature isn't claimed as reality.

### Core intelligence

| Spec item | Status | Where |
|---|---|---|
| Executive AI coordinator | ✅ real | `core/executive_ai.py` |
| Multi-step reasoning | ✅ real | `Executive.run_goal()` review loop |
| Confidence scoring | ✅ real | `core/consensus_engine.py` |
| Self-critique | ✅ real | `core/agents/critic.py` + reviewers |
| Consensus Engine | ✅ real | `core/consensus_engine.py` |
| Autonomous workflow creation | ✅ real | `core/autonomous_engine.py` |
| Multi-turn / context awareness | ✅ real | `BaseAgent` + memory + shared context |
| Project / user awareness | 🟡 partial | `MemoryAgent` reads/writes JSON store; no projector model yet |
| Uncertainty detection | 🟡 partial | critic score is the proxy |
| Explainable reasoning | 🟡 partial | reviewer LLMs return a summary; not a full causal trace |

### Multi-model

| Spec item | Status | Where |
|---|---|---|
| Multiple models simultaneously | ✅ real (via providers) | `core/llm_providers/*` |
| Dynamic model routing | 🟡 stub | heuristic per-agent; a router LLM is the next step |
| Automatic selection / benchmarking | ❌ not built | documented extension point in providers |
| Parallel inference | ❌ not built | spec'd through provider capability flags |
| Local-first inference | ✅ real | `mock` / `template` providers are offline |
| Optional cloud models | ✅ real | `http` provider is OpenAI-compatible |

### Teams & agents

| Spec item | Status | Where |
|---|---|---|
| 8 spec teams | ✅ real | `core/teams/{architecture,…,research}_team.py` |
| 15 canonical agent roles | ✅ real | `core/agents/registry.py` |
| 25+ named roles | 🟡 15 of them | the rest are placeholders denoting "*to be added*" |
| Specialist role libraries | 🟡 partial | reviewers + writers exist; domain-specialty agents don't yet |

### Knowledge / RAG

| Spec item | Status | Where |
|---|---|---|
| Local knowledge base | ✅ real | `core/knowledge/indexer.py` |
| Markdown / code indexing | ✅ real | supported extensions in `SUPPORTED_SUFFIXES` |
| PDF indexing | ❌ not built | requires a PDF text extractor |
| Semantic search (vectors) | ❌ not built | opt-in via `sentence-transformers`; not wired |
| TF-IDF search | ✅ real | `core/knowledge/search.py` |
| RAG agent | ✅ real | `core/agents/knowledge.py` |
| Citation / source tracking | 🟡 partial | source path is kept but not embedded inline |

### Plugin system

| Spec item | Status | Where |
|---|---|---|
| Plugin manifests | ✅ real | `core/plugins/manifest.py` |
| Plugin loader (in-process) | ✅ real | `core/plugins/manager.py` |
| Sample plugin | ✅ real | `plugins/git_summary/` |
| Hot reload | 🟡 env-gated | requires `ATLAS_HOT_RELOAD_PLUGINS=true` |
| Per-process subprocess sandbox | ❌ not built | next-step; would route plugins to a worker process with policy |
| Plugin marketplace | ❌ not built | spec'd only |

### Local AI / hardware

| Spec item | Status | Where |
|---|---|---|
| Hardware detection (CPU/RAM/OS) | ✅ real | `core/system/detect.py` |
| GPU detection | ✅ best-effort | `nvidia-smi` / `rocm-smi` / Metal |
| Multi-GPU scheduling | ❌ not built | provider-side concern |
| Quantisation-aware selection | 🟡 partial | detected VRAM is reported; selection policy is not yet |
| Offline mode | ✅ real | mock / template providers |

### Memory

| Spec item | Status | Where |
|---|---|---|
| Long-/short-term tiers | 🟡 partial | one `MemoryStore` per scope; tiering is explicit next step |
| Project / team / user memories | ✅ real | separate file paths via `get_settings().memory_path` |
| Append-only audit log | ✅ real | `core/audit/log.py` |
| Encrypted-at-rest memory | ✅ real (opt-in) | `core/security/crypto.py → EncryptedMemory` |

### Privacy / permissions

| Spec item | Status | Where |
|---|---|---|
| Permission gate (deny by default) | ✅ real | `core/permissions/gate.py` |
| User approval for sensitive actions | ✅ real | `git_agent.py` / `terminal.py` / `file_agent.py` consult it |
| Audit log of every grant/deny | ✅ real | `core/audit/log.py` |
| End-to-end encryption of memory | ✅ real (opt-in) | `core/security/crypto.py` |
| Secret detection in code | ✅ real | `core/agents/security_reviewer.py` |
| Dependency CVE scanning | ❌ not built | spec'd separate agent |
| Replay protection | ❌ not built | requires an identity layer |

### Integrations

| Spec item | Status | Where |
|---|---|---|
| Git (`git status`/diff/log) | ✅ real | `core/integrations/connectors/git_cli.py` |
| GitHub `gh` CLI | ✅ real | `core/integrations/connectors/github.py` |
| Docker read-only | ✅ real | `core/integrations/connectors/docker.py` |
| VS Code (`code` CLI) | ✅ real | `core/integrations/connectors/vscode.py` |
| Notion (markdown export) | ✅ real | `core/integrations/connectors/notion.py` |
| Obsidian vault reader | ✅ real | `core/integrations/connectors/obsidian.py` |
| GitLab / Kubernetes / Slack / etc | 🟡 each connector is a one-file drop-in | documented extension point |

### Code intelligence

| Spec item | Status | Where |
|---|---|---|
| Static smell detection | ✅ real | `core/agents/code_reviewer.py` |
| Security pattern review | ✅ real | `core/agents/security_reviewer.py` |
| Performance pattern review | ✅ real | `core/agents/performance_reviewer.py` |
| Dead-code / AST-level analysis | ❌ not built | requires `ast` traversal; intentionally deferred |
| Complexity analysis | ❌ not built | `radon`-class dependency not in scope |
| Auto refactor | ❌ not built | spec'd only |

### Project mgmt / analytics

| Spec item | Status | Where |
|---|---|---|
| Task model + history | ✅ real | `core/task.py` + `Executive.task_history` |
| Milestones / sprints / issues | ❌ not built | these are persistence concerns best left to a DB |
| Analytics + token usage | ❌ not built | would require live LLM token-counting |

---

## Security posture (honest)

* The Python execution tool is **stub-only by default**. Setting
  `ATLAS_ALLOW_CODE_EXECUTION=true` alone is **not** sufficient — you
  must also implement a real sandbox in `core/security/sandbox.py`
  before exec'ing user code.
* `GitAgent` / `TerminalAgent` / `FileAgent` refuse mutating actions
  unless either (a) `ATLAS_AUTO_APPROVE=true`, (b) the matching
  `ATLAS_ALLOW_<UPPER>` is set, or (c) you wire a UI prompt callback in
  place of the default deny branch.
* The audit log is **append-only**. Atlas never truncates or rotates it.
* Memory encryption uses **scrypt** + **AES-GCM**. If `cryptography`
  isn't importable the encrypted memory refuses to load rather than
  silently downgrading.

---

## Roadmap (transparent)

The features marked ❌ above are the *next obvious things to build*.
Each is a focused unit of work — see `tests/` for patterns to follow.

---

## License

MIT — see `LICENSE`.
