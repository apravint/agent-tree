# 🌲 AgentTree

> **Hierarchical Multi-Tier Agent Orchestration Engine**  
> Where expensive models think and cheaper agents do the grunt work.  
> *Match task complexity to model cost, isolate context, and verify results at every gate before proceeding.*

---

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)

## 💡 The Philosophy

> *"The trick is not spawning 20 agents and hoping they cooperate. It’s matching task complexity to model cost, isolating context, and verifying the result before the next task begins. One expensive model doing everything is a terrible default when you can build an entire execution tree around it."*

```
                 ┌────────────────────────────────┐
                 │  Tier 1: Architect             │
                 │  (Opus / Pro / High-Reasoning) │
                 │  Decomposes goal & sets gates  │
                 └───────────────┬────────────────┘
                                 │
                                 ▼
                 ┌────────────────────────────────┐
                 │  Tier 2: Coordinator           │
                 │  (Sonnet / Gemini Flash)       │
                 │  Dispatches, validates gates   │
                 └───────────────┬────────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ Tier 3: Worker 1   │ │ Tier 3: Worker 2   │ │ Tier 3: Worker 3   │
│ (Haiku / Ollama)   │ │ (Haiku / Ollama)   │ │ (Haiku / Ollama)   │
│ Code Search / Grep │ │ Implementation     │ │ Unit Test Check    │
└────────────────────┘ └────────────────────┘ └────────────────────┘
```

- **Tier 1 (Architect / Opus / Pro / Reasoning)**: Handles difficult decisions, architectural strategy, and establishes explicit verification criteria for each phase.
- **Tier 2 (Coordinator / Sonnet / Flash)**: Schedules tickets, dispatches jobs, verifies worker evidence against criteria, and enforces quality gates before advancing.
- **Tier 3 (Workers / Haiku / Flash-Lite / Ollama)**: Runs isolated, focused grunt jobs (code search, file diffs, test runs, linting) at ultra-low latency and near-zero cost.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/apravint/agent-tree.git
cd agent-tree

# Install locally via pip
pip install -e .
```

---

## ⚡ Quick Start

### 1. Run a Multi-Tier Orchestration
```bash
agent-tree "Audit audio priority rules and optimize sink latency"
```

### 2. Custom Model Tiers
Specify explicit models for each layer:
```bash
agent-tree "Refactor authentication module to support WebAuthn" \
  --tier1 claude-3-7-sonnet \
  --tier2 claude-3-5-sonnet \
  --tier3 claude-3-5-haiku
```

### 3. $0 Local-First Execution (Ollama)
Without any API keys configured, AgentTree automatically routes through local Ollama (`qwen2.5:1.5b`, `llama3`, or `deepseek-coder`):
```bash
export OLLAMA_MODEL="qwen2.5:1.5b"
agent-tree "Scan project dependencies for CVE security advisories"
```

### 4. Telemetry & History
Review past agent tree runs and execution traces:
```bash
agent-tree --history
```
Trace logs with per-step latency and verification decisions are saved to `~/.local/state/agent_tree/`.

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `TIER1_MODEL` | Architect / reasoning model | `gemini-2.5-pro` (or `qwen2.5:1.5b`) |
| `TIER2_MODEL` | Coordinator / dispatcher model | `gemini-2.5-flash` (or `qwen2.5:1.5b`) |
| `TIER3_MODEL` | Grunt worker model | `gemini-3.5-flash-lite` (or `qwen2.5:1.5b`) |
| `GEMINI_API_KEY` | Google Gemini API Key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | Optional |
| `OLLAMA_HOST` | Local Ollama endpoint | `http://localhost:11434/api/generate` |

---

## 🧪 Testing

```bash
python3 -m unittest discover tests
```

---

## 📜 License

MIT License © 2026 [Ayyappa Pravin](https://github.com/apravint)
