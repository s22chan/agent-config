import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import tomlkit

ROOT = Path(__file__).resolve().parents[1]


def run_sync(home: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "sync.py"), "--home", str(home), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def run_git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def require_git(root: Path, *arguments: str) -> None:
    result = run_git(root, *arguments)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


class SyncTest(unittest.TestCase):
    def test_bootstrap_installs_preferences_without_replacing_local_settings(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            (home / ".codex").mkdir()
            (home / ".claude").mkdir()
            codex_settings = home / ".codex/config.toml"
            claude_settings = home / ".claude/settings.json"
            codex_settings.write_text(
                'model = "local"\n\n[projects."/local/project"]\n'
                'trust_level = "trusted"\n'
            )
            claude_settings.write_text(
                json.dumps(
                    {
                        "model": "local",
                        "modelSettings": {"local": {"effortLevel": "low"}},
                        "localOnly": True,
                    }
                )
                + "\n"
            )
            uv = shutil.which("uv")
            self.assertIsNotNone(uv)
            environment = {
                "HOME": str(home),
                "PATH": f"{Path(uv).parent}:/usr/bin:/bin",
            }

            result = subprocess.run(
                ["bash", str(ROOT / "bootstrap.sh")],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((home / ".codex/.git").exists())
            self.assertFalse((home / ".claude/.git").exists())
            codex = tomlkit.parse(codex_settings.read_text()).unwrap()
            self.assertEqual(codex["model"], "local")
            self.assertEqual(
                codex["projects"]["/local/project"]["trust_level"], "trusted"
            )
            self.assertEqual(codex["approval_policy"], "on-request")
            self.assertTrue(codex["tui"]["fullscreen_transcript"])
            claude = json.loads(claude_settings.read_text())
            self.assertEqual(claude["model"], "local")
            self.assertEqual(
                claude["modelSettings"], {"local": {"effortLevel": "low"}}
            )
            self.assertTrue(claude["localOnly"])
            self.assertEqual(claude["theme"], "dark")
            self.assertEqual(claude["env"]["DISABLE_AUTOUPDATER"], "1")
            self.assertEqual(run_sync(home, "--check").returncode, 0)

    def test_sync_restores_owned_preferences_and_preserves_local_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)

            codex_path = home / ".codex/config.toml"
            codex = tomlkit.parse(codex_path.read_text())
            codex["approval_policy"] = "never"
            codex["tui"]["screen_reader_detection_done"] = True
            codex["obsolete"] = True
            codex_path.write_text(tomlkit.dumps(codex))
            codex_manifest = home / ".codex/.agent-config-manifest.json"
            manifest = json.loads(codex_manifest.read_text())
            manifest["settings"].append(["obsolete"])
            codex_manifest.write_text(json.dumps(manifest, indent=2) + "\n")

            claude_path = home / ".claude/settings.json"
            claude = json.loads(claude_path.read_text())
            claude["theme"] = "light"
            claude["localOnly"] = True
            claude_path.write_text(json.dumps(claude, indent=4) + "\n")

            result = run_sync(home, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("approval_policy", result.stderr)
            self.assertIn("theme", result.stderr)
            self.assertIn("obsolete", result.stderr)

            self.assertEqual(run_sync(home).returncode, 0)
            codex = tomlkit.parse(codex_path.read_text()).unwrap()
            self.assertEqual(codex["approval_policy"], "on-request")
            self.assertTrue(codex["tui"]["screen_reader_detection_done"])
            self.assertNotIn("obsolete", codex)
            claude = json.loads(claude_path.read_text())
            self.assertEqual(claude["theme"], "dark")
            self.assertTrue(claude["localOnly"])
            self.assertEqual(run_sync(home, "--check").returncode, 0)

    def test_adopt_existing_clones_preserves_local_state_and_backs_up_history(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            clone_inputs = {
                ".claude": (
                    "settings.json",
                    json.dumps({"model": "local", "localOnly": True}) + "\n",
                    "CLAUDE.md",
                ),
                ".codex": (
                    "config.toml",
                    'model = "local"\n',
                    "AGENTS.md",
                ),
            }
            for tool, (settings_name, settings, instructions_name) in (
                clone_inputs.items()
            ):
                clone = home / tool
                clone.mkdir()
                require_git(clone, "init", "-q")
                require_git(clone, "config", "user.name", "Migration Test")
                require_git(
                    clone, "config", "user.email", "migration@example.invalid"
                )
                (clone / settings_name).write_text(settings)
                (clone / ".gitignore").write_text(
                    f"{settings_name}\nruntime.local\nsessions/\n"
                )
                (clone / instructions_name).write_text("old instructions\n")
                (clone / "legacy.txt").write_text("committed legacy\n")
                (clone / "runtime.local").write_text("preserve runtime\n")
                (clone / "sessions").mkdir()
                (clone / "sessions/history.json").write_text("preserve session\n")
                require_git(
                    clone,
                    "add",
                    "--",
                    ".gitignore",
                    instructions_name,
                    "legacy.txt",
                )
                require_git(clone, "commit", "-q", "-m", "old config")
                (clone / "legacy.txt").write_text("dirty legacy\n")

            result = run_sync(home, "--adopt-existing-clones")

            self.assertEqual(result.returncode, 0, result.stderr)
            backup = Path(result.stdout.strip().partition("backup: ")[2])
            self.assertEqual(backup.parent, home / ".agent-config-backups")
            for tool, (settings_name, settings, instructions_name) in (
                clone_inputs.items()
            ):
                live = home / tool
                saved = backup / tool
                self.assertFalse((live / ".git").exists())
                self.assertFalse((live / "legacy.txt").exists())
                self.assertEqual(
                    (live / "runtime.local").read_text(), "preserve runtime\n"
                )
                self.assertEqual(
                    (live / "sessions/history.json").read_text(),
                    "preserve session\n",
                )
                self.assertTrue((live / instructions_name).is_file())
                self.assertTrue((saved / ".git").is_dir())
                self.assertEqual(
                    (saved / f"snapshot/{settings_name}").read_text(), settings
                )
                self.assertEqual(
                    (saved / "snapshot/legacy.txt").read_text(), "dirty legacy\n"
                )
                self.assertEqual(
                    (saved / f"snapshot/{instructions_name}").read_text(),
                    "old instructions\n",
                )
                self.assertFalse((saved / "snapshot/runtime.local").exists())
                self.assertFalse((saved / "snapshot/sessions").exists())
                metadata = json.loads((saved / "migration.json").read_text())
                self.assertIn(settings_name, metadata["snapshot"])
                self.assertIn("legacy.txt", metadata["obsolete"])
                self.assertEqual(
                    run_git(
                        live,
                        f"--git-dir={saved / '.git'}",
                        f"--work-tree={live}",
                        "status",
                        "--short",
                    ).returncode,
                    0,
                )

            claude = json.loads((home / ".claude/settings.json").read_text())
            self.assertEqual(claude["model"], "local")
            self.assertTrue(claude["localOnly"])
            codex = tomlkit.parse((home / ".codex/config.toml").read_text()).unwrap()
            self.assertEqual(codex["model"], "local")
            self.assertEqual(run_sync(home, "--check").returncode, 0)

    def test_sync_renders_instructions_and_materializes_shared_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)
            self.assertEqual(run_sync(home, "--check").returncode, 0)

            codex = (home / ".codex/AGENTS.md").read_text()
            claude = (home / ".claude/CLAUDE.md").read_text()
            shared = (ROOT / "instructions/common.md").read_text()
            self.assertIn(shared, codex)
            self.assertIn(
                "@~/agent-config/instructions/common.md", claude
            )
            self.assertNotIn(shared, claude)
            self.assertTrue(codex.startswith("<!-- Generated from ~/agent-config"))
            self.assertTrue(claude.startswith("<!-- Generated from ~/agent-config"))
            self.assertNotIn("<!-- include:", codex)
            self.assertNotIn("<!-- include:", claude)

            explorer = (home / ".claude/agents/explore-cheap.md").read_text()
            explorer_policy = (
                ROOT / "shared/prompts/explore-cheap.md"
            ).read_text()
            self.assertTrue(explorer.startswith("---\n"))
            self.assertIn("model: haiku", explorer)
            self.assertIn(explorer_policy, explorer)
            self.assertNotIn("<!-- include:", explorer)

            shared_root = ROOT / "shared"
            shared_sources = sorted(
                path for path in shared_root.rglob("*") if path.is_file()
            )
            self.assertGreater(len(shared_sources), 2)
            for source in shared_sources:
                relative = source.relative_to(shared_root)
                claude_target = home / ".claude" / relative
                self.assertTrue(claude_target.is_symlink(), claude_target)
                self.assertEqual(claude_target.resolve(), source.resolve())

                codex_target = home / ".codex" / relative
                if relative.parts[0] in {"prompts", "skills"}:
                    self.assertTrue(codex_target.is_file(), codex_target)
                    self.assertFalse(codex_target.is_symlink(), codex_target)
                    self.assertEqual(codex_target.read_bytes(), source.read_bytes())
                else:
                    target = codex_target
                    self.assertTrue(target.is_symlink(), target)
                    self.assertEqual(target.resolve(), source.resolve())

            for tool in ("codex", "claude"):
                source = ROOT / "adapters" / tool
                target_root = home / f".{tool}"
                for adapter in (
                    path for path in source.rglob("*") if path.is_file()
                ):
                    target = target_root / adapter.relative_to(source)
                    self.assertEqual(target.read_bytes(), adapter.read_bytes())
                    self.assertEqual(
                        target.stat().st_mode & 0o777,
                        adapter.stat().st_mode & 0o777,
                    )

            self.assertTrue((home / ".codex/.agent-config-manifest.json").is_file())
            self.assertTrue((home / ".claude/.agent-config-manifest.json").is_file())

    def test_shared_skills_leave_entrypoints_to_each_tool(self) -> None:
        skills = ROOT / "shared/skills"
        for skill in (path for path in skills.iterdir() if path.is_dir()):
            self.assertFalse((skill / "SKILL.md").exists(), skill)
            body = skill / "shared.md"
            self.assertTrue(body.is_file(), body)
            self.assertFalse(body.read_text().startswith("---\n"), body)

    def test_check_reports_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)
            target = home / ".codex/AGENTS.md"
            target.write_text(target.read_text() + "drift\n")

            result = run_sync(home, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn(f"out of date: {target}", result.stderr)

    def test_check_reports_shared_link_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)
            target = home / ".claude/hooks/deny-guard.sh"
            target.unlink()
            target.write_text("not the shared hook\n")

            result = run_sync(home, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn(f"out of date: {target}", result.stderr)

    def test_check_reports_shared_copy_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)
            target = home / ".codex/skills/verify-technical-evidence/shared.md"
            target.write_text("not the shared workflow\n")

            result = run_sync(home, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn(f"out of date: {target}", result.stderr)

    def test_sync_removes_only_files_recorded_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(run_sync(home).returncode, 0)
            stale = home / ".codex/obsolete-generated.txt"
            unrelated = home / ".codex/local-notes.txt"
            stale.write_text("obsolete\n")
            unrelated.write_text("keep\n")
            manifest = home / ".codex/.agent-config-manifest.json"
            value = json.loads(manifest.read_text())
            value["managed"].append("obsolete-generated.txt")
            manifest.write_text(json.dumps(value, indent=2) + "\n")

            result = run_sync(home, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn(f"stale managed file: {stale}", result.stderr)

            self.assertEqual(run_sync(home).returncode, 0)
            self.assertFalse(stale.exists())
            self.assertEqual(unrelated.read_text(), "keep\n")
            self.assertEqual(run_sync(home, "--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
