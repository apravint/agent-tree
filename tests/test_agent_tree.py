import unittest
from unittest.mock import patch
from agent_tree.orchestrator import AgentTree

class TestAgentTree(unittest.TestCase):
    def test_initialization(self):
        tree = AgentTree("Refactor authentication module", tier1_model="test-tier1")
        self.assertEqual(tree.task, "Refactor authentication module")
        self.assertEqual(tree.tier1_model, "test-tier1")
        self.assertEqual(len(tree.trace), 0)

    @patch("agent_tree.orchestrator.query_model")
    def test_run_tier1_architect_fallback_or_json(self, mock_query):
        mock_query.return_value = '{"summary": "Test Plan", "steps": [{"id": 1, "task": "Scan code", "verify": "Log output"}]}'
        tree = AgentTree("Test Task")
        plan = tree.run_tier1_architect()
        self.assertIn("steps", plan)
        self.assertEqual(len(plan["steps"]), 1)
        self.assertEqual(plan["steps"][0]["task"], "Scan code")

    @patch("agent_tree.orchestrator.query_model")
    def test_run_tier2_coordinator(self, mock_query):
        mock_query.side_effect = ["Worker executed task", "YES satisfies requirement"]
        tree = AgentTree("Test Task")
        plan = {
            "summary": "Plan",
            "steps": [{"id": 1, "task": "Calculate checksum", "verify": "Pass"}]
        }
        results = tree.run_tier2_coordinator(plan)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["verified"])

if __name__ == "__main__":
    unittest.main()
