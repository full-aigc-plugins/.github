"""Regression tests for the PAPR v1 static checker (Python stdlib only)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "check_plugin_architecture.py"
spec = importlib.util.spec_from_file_location("papr_checker", CHECKER)
policy = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(policy)


class PolicyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "AGENTS.md").write_text(
            "# Instructions\n\n" + policy.POLICY_URL + "\n",
            encoding="utf-8",
        )

    def manifest(self, name="example"):
        (self.root / "plugin.json").write_text(
            json.dumps({"$schema": policy.MANIFEST_SCHEMA, "name": name}),
            encoding="utf-8",
        )

    def skill(self, name):
        skill = self.root / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Example\n---\n\n# {name}\n",
            encoding="utf-8",
        )

    def test_no_harness_is_allowed(self):
        self.manifest()
        self.skill("example-use")
        report = policy.check(self.root)
        self.assertFalse(report.errors, report.errors)
        self.assertIn("HARNESS_OPTIONAL", " ".join(report.info))

    def test_one_discoverable_harness_is_allowed(self):
        self.manifest()
        self.skill("example-harness")
        report = policy.check(self.root)
        self.assertFalse(report.errors, report.errors)

    def test_multiple_harnesses_are_rejected(self):
        self.manifest()
        self.skill("example-harness")
        self.skill("other-harness")
        self.assertIn("MULTIPLE_HARNESSES", " ".join(policy.check(self.root).errors))

    def test_orphan_script_is_rejected(self):
        self.manifest()
        folder = self.root / "scripts"
        folder.mkdir()
        (folder / "harness.py").write_text("pass\n", encoding="utf-8")
        self.assertIn("ORPHAN_HARNESS", " ".join(policy.check(self.root).errors))

    def test_invalid_manifest_is_rejected(self):
        self.manifest("InvalidName")
        self.assertIn("MANIFEST_NAME", " ".join(policy.check(self.root).errors))

    def test_wrong_mcp_schema_is_rejected(self):
        self.manifest()
        (self.root / "mcp.json").write_text(
            json.dumps({"$schema": "invalid", "mcpServers": {}}),
            encoding="utf-8",
        )
        self.assertIn("MCP_SCHEMA", " ".join(policy.check(self.root).errors))

    def test_bootstrap_is_not_misrepresented(self):
        report = policy.check(self.root)
        self.assertFalse(report.errors, report.errors)
        self.assertIn("BOOTSTRAP_NOT_PLUGIN", " ".join(report.warnings))

    def test_missing_policy_link_is_rejected(self):
        self.manifest()
        (self.root / "AGENTS.md").write_text("# No organization policy\n")
        self.assertIn("POLICY_LINK_REQUIRED", " ".join(policy.check(self.root).errors))


if __name__ == "__main__":
    unittest.main()
