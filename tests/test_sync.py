from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def run_sync(home: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "sync.py"), "--home", str(home), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def create_remote(parent: Path, name: str) -> Path:
    seed = parent / f"{name}-seed"
    remote = parent / f"{name}.git"
    subprocess.run(["git", "init", "-q", str(seed)], check=True)
    subprocess.run(
        ["git", "-C", str(seed), "config", "user.name", "test"], check=True
    )
    subprocess.run(
        ["git", "-C", str(seed), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    (seed / ".gitignore").write_text("runtime/\n")
    subprocess.run(["git", "-C", str(seed), "add", ".gitignore"], check=True)
    subprocess.run(["git", "-C", str(seed), "commit", "-qm", "seed"], check=True)
    subprocess.run(
        ["git", "clone", "-q", "--bare", str(seed), str(remote)], check=True
    )
    return remote


class SyncTest(unittest.TestCase):
    def test_bootstrap_clones_tool_configs_and_syncs_shared_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            codex_remote = create_remote(root, "codex")
            claude_remote = create_remote(root, "claude")
            environment = {
                "HOME": str(home),
                "PATH": "/usr/bin:/bin",
                "S22CHAN_CODEX_REPO": str(codex_remote),
                "S22CHAN_CLAUDE_REPO": str(claude_remote),
            }

            result = subprocess.run(
                ["bash", str(ROOT / "bootstrap.sh")],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((home / ".codex/.git").is_dir())
            self.assertTrue((home / ".claude/.git").is_dir())
            self.assertEqual(run_sync(home, "--check").returncode, 0)

    def test_sync_renders_instructions_and_links_shared_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)
            self.assertEqual(run_sync(home, "--check").returncode, 0)

            codex = (home / ".codex/AGENTS.md").read_text()
            claude = (home / ".claude/CLAUDE.md").read_text()
            shared = (ROOT / "instructions/implementation.md").read_text()
            self.assertIn(shared, codex)
            self.assertIn(shared, claude)
            self.assertTrue(codex.startswith("<!-- Generated from ~/agent-config"))
            self.assertTrue(claude.startswith("<!-- Generated from ~/agent-config"))
            self.assertNotIn("<!-- include:", codex)
            self.assertNotIn("<!-- include:", claude)

            skill = home / ".codex/skills/design-diagnostic-visualizations/SKILL.md"
            self.assertTrue(skill.is_symlink())
            self.assertEqual(
                skill.resolve(),
                (
                    ROOT
                    / "shared/skills/design-diagnostic-visualizations/SKILL.md"
                ).resolve(),
            )

    def test_check_reports_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)
            target = home / ".codex/AGENTS.md"
            target.write_text(target.read_text() + "drift\n")

            result = run_sync(home, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn(f"out of date: {target}", result.stderr)


if __name__ == "__main__":
    unittest.main()
