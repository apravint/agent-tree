import sys
import os
import argparse
from agent_tree.orchestrator import AgentTree, STATE_DIR, BOLD, NC

def main():
    parser = argparse.ArgumentParser(
        description="AgentTree: Hierarchical Multi-Tier Agent Orchestration Engine"
    )
    parser.add_argument("task", nargs="*", help="Goal or task description")
    parser.add_argument("--tier1", help="Tier 1 Architect model (e.g. claude-3-7-sonnet, gemini-2.5-pro)")
    parser.add_argument("--tier2", help="Tier 2 Coordinator model (e.g. claude-3-5-sonnet, gemini-2.5-flash)")
    parser.add_argument("--tier3", help="Tier 3 Grunt Worker model (e.g. claude-3-5-haiku, gemini-3.5-flash-lite, qwen2.5:1.5b)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed telemetry traces")
    parser.add_argument("--history", action="store_true", help="Show past agent tree runs")
    args = parser.parse_args()

    if args.history:
        if os.path.exists(STATE_DIR):
            runs = sorted(os.listdir(STATE_DIR), reverse=True)
            print(f"{BOLD}Agent Tree Past Executions:{NC}")
            for r in runs[:10]:
                print(f"  • {r}")
        else:
            print("No execution history found.")
        return

    if not args.task:
        parser.print_help()
        print("\nExample:")
        print("  agent-tree 'Audit database connection pool leaks and verify fixes with unit tests'")
        sys.exit(1)

    task_str = " ".join(args.task)
    tree = AgentTree(
        task=task_str,
        tier1_model=args.tier1,
        tier2_model=args.tier2,
        tier3_model=args.tier3,
        verbose=args.verbose
    )
    plan = tree.run_tier1_architect()
    results = tree.run_tier2_coordinator(plan)
    tree.finalize_review(results)

if __name__ == "__main__":
    main()
