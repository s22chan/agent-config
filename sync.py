#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
INSTRUCTIONS = ROOT / "instructions"
SHARED = ROOT / "shared"
ADAPTERS = ROOT / "adapters"
INCLUDE = re.compile(r'^<!-- include: ([^/][^>]*) -->$')
# Codex rejects instruction-support symlinks whose targets sit outside the
# active workspace, so referenced assets must be copied under its config root.
CODEX_COPY_ROOTS = {"prompts", "skills"}
GENERATED_HEADER = (
    "<!-- Generated from ~/agent-config; edit the source templates there. -->\n"
)
MANIFEST_NAME = ".agent-config-manifest.json"
TOOL_ADAPTERS = {
    ".codex": ADAPTERS / "codex",
    ".claude": ADAPTERS / "claude",
}
TARGETS = {
    Path(".codex/AGENTS.md"): (INSTRUCTIONS / "codex.md.in", True),
    Path(".claude/CLAUDE.md"): (INSTRUCTIONS / "claude.md.in", True),
    Path(".claude/agents/explore-cheap.md"): (
        INSTRUCTIONS / "claude-explore-cheap.md.in",
        False,
    ),
}


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
    return json.dumps({"managed": sorted(managed)}, indent=2) + "\n"


def read_manifest(home: Path, tool: str) -> set[str]:
    path = home / tool / MANIFEST_NAME
    if not path.is_file():
        return set()
    try:
        value = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return set()
    managed = value.get("managed")
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
        manifest = home / tool / MANIFEST_NAME
        expected = expected_manifest(home, tool)
        if not manifest.is_file() or manifest.read_text() != expected:
            errors.append(f"out of date: {manifest}")
        expected_paths = set(json.loads(expected)["managed"])
        for relative in sorted(read_manifest(home, tool) - expected_paths):
            stale = home / tool / relative
            if stale.exists() or stale.is_symlink():
                errors.append(f"stale managed file: {stale}")
    return errors


def sync(home: Path) -> None:
    for tool in TOOL_ADAPTERS:
        expected_paths = set(json.loads(expected_manifest(home, tool))["managed"])
        for relative in sorted(read_manifest(home, tool) - expected_paths):
            remove_stale(home, tool, relative)
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args()
    if args.check:
        errors = check(args.home)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        return 0
    sync(args.home)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
