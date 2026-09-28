#!/usr/bin/env -S uv run --frozen --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["tomlkit==0.15.1"]
# ///

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import tomlkit

ROOT = Path(__file__).resolve().parent
INSTRUCTIONS = ROOT / "instructions"
SHARED = ROOT / "shared"
ADAPTERS = ROOT / "adapters"
PREFERENCES = ROOT / "preferences"
INCLUDE = re.compile(r'^<!-- include: ([^/][^>]*) -->$')
# Codex rejects instruction-support symlinks whose targets sit outside the
# active workspace, so referenced assets must be copied under its config root.
CODEX_COPY_ROOTS = {"prompts", "skills"}
GENERATED_HEADER = (
    "<!-- Generated from ~/agent-config; edit sources there, then run "
    "~/agent-config/bootstrap.sh. -->\n"
)
MANIFEST_NAME = ".agent-config-manifest.json"
TOOL_ADAPTERS = {
    ".codex": ADAPTERS / "codex",
    ".claude": ADAPTERS / "claude",
}
SETTINGS = {
    ".codex": (Path("config.toml"), PREFERENCES / "codex.toml", "toml"),
    ".claude": (Path("settings.json"), PREFERENCES / "claude.json", "json"),
}
TARGETS = {
    Path(".codex/AGENTS.md"): (INSTRUCTIONS / "codex.md.in", True),
    Path(".claude/CLAUDE.md"): (INSTRUCTIONS / "claude.md.in", True),
    Path(".claude/agents/explore-cheap.md"): (
        INSTRUCTIONS / "claude-explore-cheap.md.in",
        False,
    ),
}


@dataclass(frozen=True)
class ConfigClone:
    root: Path
    tracked_paths: tuple[Path, ...]


def render(template: Path, *, add_header: bool = True) -> str:
    rendered = [GENERATED_HEADER] if add_header else []
    for line in template.read_text().splitlines(keepends=True):
        match = INCLUDE.fullmatch(line.rstrip("\n"))
        if match is None:
            rendered.append(line)
            continue
        include = (template.parent / match.group(1)).resolve()
        if not include.is_relative_to(ROOT):
            raise ValueError(f"include escapes source repository: {include}")
        text = include.read_text()
        rendered.append(text if text.endswith("\n") else text + "\n")
    return "".join(rendered)


def replace_bytes(path: Path, content: bytes, mode: int = 0o640) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, delete=False, prefix=f".{path.name}.",
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    os.chmod(temporary_path, mode)
    os.replace(temporary_path, path)


def replace_file(path: Path, content: str, mode: int = 0o640) -> None:
    replace_bytes(path, content.encode(), mode)


def shared_sources() -> list[Path]:
    return sorted(path for path in SHARED.rglob("*") if path.is_file())


def adapter_sources() -> list[tuple[str, Path, Path]]:
    sources = []
    for tool, root in TOOL_ADAPTERS.items():
        sources.extend(
            (tool, path.relative_to(root), path)
            for path in sorted(root.rglob("*"))
            if path.is_file()
        )
    return sources


def expected_links(home: Path) -> dict[Path, Path]:
    links = {}
    for source in shared_sources():
        relative = source.relative_to(SHARED)
        links[home / ".claude" / relative] = source
        if relative.parts[0] not in CODEX_COPY_ROOTS:
            links[home / ".codex" / relative] = source
    return links


def expected_copies(home: Path) -> dict[Path, Path]:
    copies = {}
    for source in shared_sources():
        relative = source.relative_to(SHARED)
        if relative.parts[0] in CODEX_COPY_ROOTS:
            copies[home / ".codex" / relative] = source
    for tool, relative, source in adapter_sources():
        target = home / tool / relative
        if target in copies:
            raise ValueError(f"multiple generated sources own {target}")
        copies[target] = source
    return copies


def load_preferences(tool: str) -> dict:
    _, source, file_type = SETTINGS[tool]
    if file_type == "toml":
        return tomlkit.parse(source.read_text()).unwrap()
    if file_type != "json":
        raise ValueError(f"unsupported settings type: {file_type}")
    value = json.loads(source.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"preference source must contain an object: {source}")
    return value


def preference_paths(
    value: Mapping, prefix: tuple[str, ...] = ()
) -> list[tuple[str, ...]]:
    paths = []
    for key, child in value.items():
        path = prefix + (key,)
        if isinstance(child, Mapping) and child:
            paths.extend(preference_paths(child, path))
        else:
            paths.append(path)
    return paths


def read_settings(path: Path, file_type: str):
    if not path.is_file():
        if file_type == "toml":
            return tomlkit.document()
        if file_type == "json":
            return {}
        raise ValueError(f"unsupported settings type: {file_type}")
    if file_type == "toml":
        return tomlkit.parse(path.read_text())
    if file_type != "json":
        raise ValueError(f"unsupported settings type: {file_type}")
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"settings file must contain an object: {path}")
    return value


def plain_value(value):
    unwrap = getattr(value, "unwrap", None)
    return unwrap() if unwrap is not None else value


def get_path(settings: Mapping, path: tuple[str, ...]):
    current = settings
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            return False, None
        current = current[key]
    return True, plain_value(current)


def set_path(
    settings: MutableMapping,
    path: tuple[str, ...],
    value,
    file_type: str,
) -> bool:
    found, current = get_path(settings, path)
    if found and current == value:
        return False
    parent = settings
    for key in path[:-1]:
        if key not in parent:
            if file_type == "toml":
                parent[key] = tomlkit.table()
            elif file_type == "json":
                parent[key] = {}
            else:
                raise ValueError(f"unsupported settings type: {file_type}")
        child = parent[key]
        if not isinstance(child, MutableMapping):
            parent_path = ".".join(path[:-1])
            raise ValueError(f"cannot manage nested preference below {parent_path}")
        parent = child
    parent[path[-1]] = value
    return True


def remove_path(settings: MutableMapping, path: tuple[str, ...]) -> bool:
    parents = []
    current = settings
    for key in path[:-1]:
        if key not in current or not isinstance(current[key], MutableMapping):
            return False
        parents.append((current, key))
        current = current[key]
    if path[-1] not in current:
        return False
    del current[path[-1]]
    for parent, key in reversed(parents):
        if parent[key]:
            break
        del parent[key]
    return True


def dump_settings(settings, file_type: str) -> str:
    if file_type == "toml":
        return tomlkit.dumps(settings)
    if file_type == "json":
        return json.dumps(settings, indent=4) + "\n"
    raise ValueError(f"unsupported settings type: {file_type}")


def apply_preferences(home: Path, tool: str) -> None:
    relative, _, file_type = SETTINGS[tool]
    target = home / tool / relative
    settings = read_settings(target, file_type)
    preferences = load_preferences(tool)
    expected_paths = set(preference_paths(preferences))
    changed = False
    for path in read_managed_settings(home, tool) - expected_paths:
        changed |= remove_path(settings, path)
    for path in preference_paths(preferences):
        _, value = get_path(preferences, path)
        changed |= set_path(settings, path, value, file_type)
    if changed:
        mode = target.stat().st_mode & 0o777 if target.is_file() else 0o600
        replace_file(target, dump_settings(settings, file_type), mode)


def check_preferences(home: Path, tool: str) -> list[str]:
    relative, _, file_type = SETTINGS[tool]
    target = home / tool / relative
    try:
        settings = read_settings(target, file_type)
    except (json.JSONDecodeError, tomlkit.exceptions.ParseError, ValueError) as error:
        return [f"invalid settings: {target}: {error}"]
    errors = []
    preferences = load_preferences(tool)
    expected_paths = set(preference_paths(preferences))
    for path in preference_paths(preferences):
        found, actual = get_path(settings, path)
        _, expected = get_path(preferences, path)
        if not found or actual != expected:
            errors.append(f"out of date preference: {target}: {'.'.join(path)}")
    for path in read_managed_settings(home, tool) - expected_paths:
        found, _ = get_path(settings, path)
        if found:
            errors.append(f"stale managed preference: {target}: {'.'.join(path)}")
    return errors


def expected_manifest(home: Path, tool: str) -> str:
    tool_root = home / tool
    managed = {
        (home / relative).relative_to(tool_root).as_posix()
        for relative in TARGETS
        if (home / relative).is_relative_to(tool_root)
    }
    managed.update(
        target.relative_to(tool_root).as_posix()
        for target in expected_links(home)
        if target.is_relative_to(tool_root)
    )
    managed.update(
        target.relative_to(tool_root).as_posix()
        for target in expected_copies(home)
        if target.is_relative_to(tool_root)
    )
    settings = [list(path) for path in preference_paths(load_preferences(tool))]
    return json.dumps(
        {"managed": sorted(managed), "settings": settings}, indent=2
    ) + "\n"


def read_manifest(home: Path, tool: str) -> dict:
    path = home / tool / MANIFEST_NAME
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def read_managed_files(home: Path, tool: str) -> set[str]:
    managed = read_manifest(home, tool).get("managed")
    if not isinstance(managed, list):
        return set()
    paths = set()
    for item in managed:
        if not isinstance(item, str):
            return set()
        relative = Path(item)
        if relative.is_absolute() or ".." in relative.parts:
            return set()
        paths.add(item)
    return paths


def read_managed_settings(home: Path, tool: str) -> set[tuple[str, ...]]:
    managed = read_manifest(home, tool).get("settings")
    if not isinstance(managed, list):
        return set()
    paths = set()
    for item in managed:
        if (
            not isinstance(item, list)
            or not item
            or any(not isinstance(part, str) or not part for part in item)
        ):
            return set()
        paths.add(tuple(item))
    return paths


def remove_stale(home: Path, tool: str, relative: str) -> None:
    tool_root = (home / tool).resolve()
    stale = home / tool / relative
    if not stale.parent.resolve().is_relative_to(tool_root):
        raise ValueError(f"managed path escapes {tool_root}: {relative}")
    if stale.is_file() or stale.is_symlink():
        stale.unlink()


def check(home: Path) -> list[str]:
    errors = []
    for relative, (template, add_header) in TARGETS.items():
        target = home / relative
        expected = render(template, add_header=add_header)
        if not target.is_file() or target.read_text() != expected:
            errors.append(f"out of date: {target}")
    for target, source in expected_links(home).items():
        relative_source = os.path.relpath(source, start=target.parent)
        if not target.is_symlink() or os.readlink(target) != relative_source:
            errors.append(f"out of date: {target}")
    for target, source in expected_copies(home).items():
        expected_mode = source.stat().st_mode & 0o777
        if (
            target.is_symlink()
            or not target.is_file()
            or target.read_bytes() != source.read_bytes()
            or target.stat().st_mode & 0o777 != expected_mode
        ):
            errors.append(f"out of date: {target}")
    for tool in TOOL_ADAPTERS:
        errors.extend(check_preferences(home, tool))
        manifest = home / tool / MANIFEST_NAME
        expected = expected_manifest(home, tool)
        if not manifest.is_file() or manifest.read_text() != expected:
            errors.append(f"out of date: {manifest}")
        expected_paths = set(json.loads(expected)["managed"])
        for relative in sorted(read_managed_files(home, tool) - expected_paths):
            stale = home / tool / relative
            if stale.exists() or stale.is_symlink():
                errors.append(f"stale managed file: {stale}")
    return errors


def sync(home: Path) -> None:
    for tool in TOOL_ADAPTERS:
        expected_paths = set(json.loads(expected_manifest(home, tool))["managed"])
        for relative in sorted(read_managed_files(home, tool) - expected_paths):
            remove_stale(home, tool, relative)
        apply_preferences(home, tool)
    for relative, (template, add_header) in TARGETS.items():
        content = render(template, add_header=add_header)
        replace_file(home / relative, content)
    for target, source in expected_links(home).items():
        target.parent.mkdir(parents=True, exist_ok=True)
        relative_source = os.path.relpath(source, start=target.parent)
        if target.is_symlink() and os.readlink(target) == relative_source:
            continue
        if target.exists() or target.is_symlink():
            target.unlink()
        target.symlink_to(relative_source)
    for target, source in expected_copies(home).items():
        expected_mode = source.stat().st_mode & 0o777
        if (
            not target.is_symlink()
            and target.is_file()
            and target.read_bytes() == source.read_bytes()
            and target.stat().st_mode & 0o777 == expected_mode
        ):
            continue
        replace_bytes(target, source.read_bytes(), expected_mode)
    for tool in TOOL_ADAPTERS:
        replace_file(
            home / tool / MANIFEST_NAME,
            expected_manifest(home, tool),
        )


def git_output(root: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        error = os.fsdecode(result.stderr).strip()
        raise RuntimeError(f"git failed for {root}: {error}")
    return result.stdout


def find_config_clones(home: Path) -> list[ConfigClone]:
    clones = []
    for tool in TOOL_ADAPTERS:
        root = home / tool
        git_metadata = root / ".git"
        if not git_metadata.exists() and not git_metadata.is_symlink():
            continue
        top_level = Path(
            os.fsdecode(git_output(root, "rev-parse", "--show-toplevel")).strip()
        )
        if top_level.resolve() != root.resolve():
            raise ValueError(
                f"refusing to adopt {root}: repository root is {top_level}"
            )
        tracked_paths = []
        for raw_path in git_output(root, "ls-files", "-z").split(b"\0"):
            if not raw_path:
                continue
            relative = Path(os.fsdecode(raw_path))
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"tracked path escapes {root}: {relative}")
            source = root / relative
            if source.exists() and not source.is_file() and not source.is_symlink():
                raise ValueError(
                    f"refusing to adopt non-file tracked path: {source}"
                )
            tracked_paths.append(relative)
        clones.append(ConfigClone(root, tuple(tracked_paths)))
    return clones


def create_backup_root(home: Path) -> Path:
    parent = home / ".agent-config-backups"
    parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(tempfile.mkdtemp(prefix=f"adopt-{timestamp}-", dir=parent))


def copy_config_path(source: Path, target: Path) -> bool:
    if not source.exists() and not source.is_symlink():
        return False
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if source.is_symlink():
        target.symlink_to(os.readlink(source))
    else:
        shutil.copy2(source, target)
    return True


def owned_config_paths(home: Path, tool: str) -> set[Path]:
    managed = {
        Path(relative)
        for relative in json.loads(expected_manifest(home, tool))["managed"]
    }
    settings_path, _, _ = SETTINGS[tool]
    return managed | {settings_path, Path(MANIFEST_NAME)}


def obsolete_tracked_paths(home: Path, clone: ConfigClone) -> set[Path]:
    return set(clone.tracked_paths) - owned_config_paths(home, clone.root.name)


def remove_empty_parents(path: Path, root: Path) -> None:
    while path != root:
        try:
            path.rmdir()
        except OSError:
            return
        path = path.parent


def adopt_existing_clones(home: Path) -> Path | None:
    clones = find_config_clones(home)
    if not clones:
        sync(home)
        return None

    backup = create_backup_root(home)
    obsolete_by_root = {
        clone.root: obsolete_tracked_paths(home, clone) for clone in clones
    }
    for clone in clones:
        clone_backup = backup / clone.root.name
        snapshot_backup = clone_backup / "snapshot"
        snapshot_paths = set(clone.tracked_paths) | owned_config_paths(
            home, clone.root.name
        )
        snapshot = []
        missing = []
        for relative in sorted(snapshot_paths):
            if copy_config_path(clone.root / relative, snapshot_backup / relative):
                snapshot.append(relative.as_posix())
            else:
                missing.append(relative.as_posix())
        metadata = {
            "source": str(clone.root),
            "tracked": [path.as_posix() for path in clone.tracked_paths],
            "snapshot": snapshot,
            "missing": missing,
            "obsolete": sorted(
                path.as_posix() for path in obsolete_by_root[clone.root]
            ),
        }
        replace_file(
            clone_backup / "migration.json",
            json.dumps(metadata, indent=2) + "\n",
            mode=0o600,
        )

    sync(home)
    errors = check(home)
    if errors:
        raise RuntimeError(
            f"synchronized configuration did not validate; backup is {backup}:\n"
            + "\n".join(errors)
        )

    for clone in clones:
        clone_backup = backup / clone.root.name
        shutil.move(str(clone.root / ".git"), str(clone_backup / ".git"))
        for relative in sorted(obsolete_by_root[clone.root]):
            stale = clone.root / relative
            if stale.is_file() or stale.is_symlink():
                stale.unlink()
                remove_empty_parents(stale.parent, clone.root)

    errors = check(home)
    if errors:
        raise RuntimeError(
            f"adopted configuration did not validate; backup is {backup}:\n"
            + "\n".join(errors)
        )
    return backup


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true")
    action.add_argument("--adopt-existing-clones", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args()
    if args.check:
        errors = check(args.home)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        return 0
    if args.adopt_existing_clones:
        backup = adopt_existing_clones(args.home)
        if backup is None:
            print("no existing ~/.claude or ~/.codex clones found; synchronized")
        else:
            print(f"adopted existing config clones; backup: {backup}")
        return 0
    sync(args.home)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
