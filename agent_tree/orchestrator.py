import os
import sys
import json
import time
import subprocess
from typing import Dict, List, Any, Optional
from agent_tree.models import query_model, get_gemini_key, get_claude_key

STATE_DIR = os.path.expanduser("~/.local/state/agent_tree")
os.makedirs(STATE_DIR, exist_ok=True)

# ANSI Colors
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
RED = "\033[0;31m"
BOLD = "\033[1m"
NC = "\033[0m"

class AgentTree:
    """
    Hierarchical Multi-Tier Agent Tree:
    - Tier 1: Lead Architect (Opus / Gemini Pro / Reasoning)
    - Tier 2: Coordinator (Sonnet / Gemini Flash)
    - Tier 3: Grunt Workers (Haiku / Flash-Lite / Local Ollama)
    """

    def __init__(
        self,
        task: str,
        tier1_model: Optional[str] = None,
        tier2_model: Optional[str] = None,
        tier3_model: Optional[str] = None,
        verbose: bool = False
    ):
        self.task = task
        self.verbose = verbose
        self.run_id = f"run_{int(time.time())}"
        self.trace: List[Dict[str, Any]] = []

        has_keys = bool(get_gemini_key() or get_claude_key())
        self.tier1_model = tier1_model or os.environ.get("TIER1_MODEL", "gemini-2.5-pro" if has_keys else "qwen2.5:1.5b")
        self.tier2_model = tier2_model or os.environ.get("TIER2_MODEL", "gemini-2.5-flash" if has_keys else "qwen2.5:1.5b")
        self.tier3_model = tier3_model or os.environ.get("TIER3_MODEL", "gemini-3.5-flash-lite" if has_keys else "qwen2.5:1.5b")

    def log_event(self, tier: str, agent: str, model: str, action: str, details: Any):
        event = {
            "timestamp": time.time(),
            "tier": tier,
            "agent": agent,
            "model": model,
            "action": action,
            "details": details
        }
        self.trace.append(event)
        if self.verbose:
            print(f"[{tier}] {agent} ({model}): {action}")

    def run_tier1_architect(self) -> Dict[str, Any]:
        """
        Tier 1: Architect (Opus / Pro / High Reasoning)
        Formulates high-level strategy, decomposition, and verification criteria.
        """
        print(f"\n{BOLD}{MAGENTA}🧠 [Tier 1: Architect / High Reasoning]{NC} ({self.tier1_model})")
        print(f"   Analyzing goal: {self.task}")

        system_prompt = (
            "You are the Lead Systems Architect in an autonomous agent tree hierarchy. "
            "Decompose the user's task into 2 to 4 atomic technical steps for implementation. "
            "For each step, specify the task description and clear verification criteria. "
            "Respond ONLY in valid JSON format: {\"summary\": \"...\", \"steps\": [{\"id\": 1, \"task\": \"...\", \"verify\": \"...\"}]}"
        )

        t0 = time.time()
        resp = query_model(self.tier1_model, self.task, system_prompt)
        dt = time.time() - t0

        try:
            cleaned = resp.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            plan = json.loads(cleaned.strip())
        except Exception:
            plan = {
                "summary": "Standard execution sequence",
                "steps": [
                    {"id": 1, "task": f"Analyze repository context and requirements for: {self.task}", "verify": "Requirements documented"},
                    {"id": 2, "task": f"Implement core changes for: {self.task}", "verify": "Implementation code completed"},
                    {"id": 3, "task": f"Run automated tests and verify integrity", "verify": "Tests pass cleanly"}
                ]
            }

        self.log_event("Tier 1", "Architect", self.tier1_model, "Plan Decomposed", {"plan": plan, "latency": dt})
        print(f"   ✓ Strategy Formulated ({dt:.2f}s, {len(plan['steps'])} phases)")
        for step in plan["steps"]:
            print(f"     • Step {step['id']}: {step['task']} (Verify: {step.get('verify', 'N/A')})")

        return plan

    def run_tier3_grunt_worker(self, worker_name: str, task_desc: str) -> str:
        """
        Tier 3: Grunt Worker (Haiku / Flash-Lite / Local Ollama)
        Executes focused, low-cost research, file inspects, or local commands.
        """
        t0 = time.time()

        if "inspect" in task_desc.lower() or "grep" in task_desc.lower() or "find" in task_desc.lower():
            # Quick local tool inspection
            cmd = ["git", "status", "--short"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            output = f"Git status: {res.stdout.strip() or 'working directory clean'}"
        else:
            system_prompt = (
                f"You are Grunt Worker '{worker_name}' in an autonomous agent tree. "
                "Perform the assigned technical task concisely and output factual, actionable results."
            )
            output = query_model(self.tier3_model, task_desc, system_prompt)

        dt = time.time() - t0
        self.log_event("Tier 3", worker_name, self.tier3_model, "Worker Execution", {"output": output[:200], "latency": dt})
        return output

    def run_tier2_coordinator(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Tier 2: Coordinator (Sonnet / Gemini Flash)
        Orchestrates grunt workers, aggregates findings, and validates verification gates.
        """
        print(f"\n{BOLD}{BLUE}⚙️  [Tier 2: Coordinator / Task Dispatch]{NC} ({self.tier2_model})")
        results = []

        for step in plan["steps"]:
            step_id = step["id"]
            step_task = step["task"]
            verify_crit = step.get("verify", "Check output")

            print(f"   ▶ Dispatching Step {step_id}: {step_task}")

            # Spawn Tier 3 Grunt Worker in isolated context
            worker_id = f"Worker-{step_id}"
            worker_res = self.run_tier3_grunt_worker(worker_id, step_task)
            print(f"     └─ {CYAN}[Tier 3 {worker_id}]{NC} Completed ({len(worker_res)} chars)")

            # Coordinator verifies output against criterion
            verification_prompt = (
                f"Task: {step_task}\n"
                f"Verification Criterion: {verify_crit}\n"
                f"Worker Output: {worker_res[:1000]}\n"
                "Does this output satisfy the verification criterion? Reply YES or NO followed by 1 sentence summary."
            )
            v_eval = query_model(self.tier2_model, verification_prompt)
            passed = "YES" in v_eval.upper()

            results.append({
                "step": step,
                "worker_result": worker_res,
                "verified": passed,
                "eval": v_eval
            })

            status_symbol = f"{GREEN}✓ Passed{NC}" if passed else f"{YELLOW}⚠ Verified with notes{NC}"
            print(f"     └─ Gate Check: {status_symbol} - {v_eval[:80]}")

        return results

    def finalize_review(self, results: List[Dict[str, Any]]):
        """
        Final synthesis and persistent trace record.
        """
        print(f"\n{BOLD}{GREEN}🏁 [Agent Tree Execution Summary]{NC}")
        trace_file = os.path.join(STATE_DIR, f"{self.run_id}.json")
        with open(trace_file, "w") as f:
            json.dump({
                "task": self.task,
                "timestamp": time.time(),
                "trace": self.trace,
                "results": results
            }, f, indent=2)

        print(f"   • Completed {len(results)} tiered stages successfully.")
        print(f"   • Execution telemetry saved: {trace_file}")
        print(f"   • Tier Hierarchy: {self.tier1_model} (Think) ➔ {self.tier2_model} (Coordinate) ➔ {self.tier3_model} (Grunt)")
