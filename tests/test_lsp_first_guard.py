import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "shared" / "hooks" / "lsp-first-guard.py"

SOURCE = """\
def create_submitit_executor():
    pass


class SLURMBackend:
    def submit_array(self):
        pass


class LocalBackend:
    def submit_array(self):
        pass


class A:
    def submit_array(self):
        pass


class B:
    def submit_array(self):
        pass


def main():
    pass
"""


class LspFirstGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name)
        (cls.repo / "mod.py").write_text(SOURCE)
        (cls.repo / "notes.md").write_text("create_submitit_executor is documented here\n")
        for command in (["init", "-q"], ["add", "."], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
            subprocess.run(["git", *command], cwd=cls.repo, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_hook(self, tool, tool_input):
        payload = {"tool_name": tool, "tool_input": tool_input, "cwd": str(self.repo)}
        out = subprocess.run(
            ["python3", str(HOOK)], input=json.dumps(payload), capture_output=True, text=True, check=True
        ).stdout
        if not out:
            return "allow", ""
        decision = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        return "deny", decision["permissionDecisionReason"]

    def grep(self, pattern, **kwargs):
        return self.run_hook("Grep", {"pattern": pattern, **kwargs})

    def bash(self, command):
        return self.run_hook("Bash", {"command": command})

    def test_denies_a_defined_symbol_in_every_search_surface(self):
        for decision in (
            self.grep("create_submitit_executor"),
            self.grep("create_submitit_executor(", glob="*.py"),
            self.grep(r"\bcreate_submitit_executor\b", type="py"),
            self.bash("rg -n create_submitit_executor projects"),
            self.bash("git grep -n create_submitit_executor -- '*.py'"),
            self.bash("grep -rn 'create_submitit_executor' ."),
            self.bash("cd x && rg -e create_submitit_executor | head"),
            self.run_hook("Glob", {"pattern": "**/*create_submitit_executor*"}),
        ):
            self.assertEqual(decision[0], "deny")
            self.assertIn("LSP", decision[1])

    def test_a_definition_lookup_points_to_workspace_symbol(self):
        decision, reason = self.grep(r"def\s+create_submitit_executor")
        self.assertEqual(decision, "deny")
        self.assertIn("workspaceSymbol", reason)
        self.assertIn("workspaceSymbol", self.grep("class SLURMBackend")[1])

    def test_a_reference_search_points_to_find_references(self):
        self.assertIn("findReferences", self.grep("create_submitit_executor")[1])

    def test_denies_a_symbol_inside_an_alternation_and_a_method_defined_in_many_classes(self):
        self.assertEqual(self.grep(r"foo_bar_baz|create_submitit_executor")[0], "deny")
        self.assertEqual(self.grep("submit_array")[0], "deny")

    def test_allows_literals_names_the_repo_does_not_define_and_ordinary_words(self):
        for decision in (
            self.grep("ESMCFold"),
            self.grep("slurm_job_name"),
            self.grep("TODO"),
            self.grep("main"),
            self.grep("DEFAULT_PROJECT"),
            self.grep("job name suffix"),
            self.grep("update_parameters"),
            self.bash("rg -n ESMCFold projects"),
            self.bash("ls -la"),
            self.bash("echo create_submitit_executor"),
        ):
            self.assertEqual(decision[0], "allow")

    def test_allows_non_python_targets(self):
        for decision in (
            self.grep("create_submitit_executor", glob="*.md"),
            self.grep("create_submitit_executor", type="md"),
            self.grep("create_submitit_executor", path="docs/notes.md"),
            self.bash("rg create_submitit_executor --glob '*.md' ."),
            self.bash("grep -rn create_submitit_executor --include='*.sh' ."),
            self.run_hook("Glob", {"pattern": "**/*.md"}),
        ):
            self.assertEqual(decision[0], "allow")

    def test_a_call_it_cannot_parse_is_allowed(self):
        self.assertEqual(self.bash("rg 'unterminated create_submitit_executor")[0], "allow")


if __name__ == "__main__":
    unittest.main()
