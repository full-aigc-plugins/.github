#!/usr/bin/env python3
"""PAPR v1: fast, dependency-free static checks for Partme Agent Plugin repos.

Checks enforce only machine-verifiable boundaries. They DO NOT certify actual
Agent routing, side-effect safety, or portable schema completeness.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

POLICY_URL = (
    "https://github.com/full-aigc-plugins/.github/blob/main/"
    "docs/standards/partme-agent-plugin-architecture-rules-v1.md"
)
POLICY_TOKEN = "partme-agent-plugin-architecture-rules-v1.md"
MANIFEST_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
VALID_MANIFEST_FIELDS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
PORTABLE_FORBIDDEN = {"commands", "hooks", "skills", "mcpServers"}
PLUGIN_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.\-]{0,62}[a-z0-9])?$")
SINGLE_DOT_DASH = re.compile(r"--|\.\.")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, code: str, message: str) -> None:
        self.errors.append(f"{code}: {message}")

    def warn(self, code: str, message: str) -> None:
        self.warnings.append(f"{code}: {message}")

    def note(self, code: str, message: str) -> None:
        self.info.append(f"{code}: {message}")

    def print(self) -> None:
        for label, items in (("ERROR", self.errors), ("WARN", self.warnings), ("INFO", self.info)):
            for item in items:
                print(f"::{label.lower()}::{item}")
        print(f"PAPR v1: {len(self.errors)} error(s), "
              f"{len(self.warnings)} warning(s), {len(self.info)} note(s)")


def read_json(path: Path, report: Report) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        report.error("JSON_INVALID", f"{path.name}: {exc}")
        return None


def check_manifest(root: Path, report: Report) -> str | None:
    path = root / "plugin.json"
    if not path.is_file():
        # Very early incubating repo: no manifest, no plugin components.
        if not any((root / name).exists() for name in ("skills", "mcp.json", "src")):
            report.warn("BOOTSTRAP_NOT_PLUGIN",
                        "plugin.json absent; this repository is not yet an Agent Plugins package. "
                        "Create a manifest before claiming compatibility.")
        else:
            report.error("MANIFEST_REQUIRED",
                         "plugin.json is missing from an initialized plugin package.")
        return None

    obj = read_json(path, report)
    if not isinstance(obj, dict):
        report.error("MANIFEST_OBJECT", "plugin.json must be a JSON object")
        return None
    if obj.get("$schema") != MANIFEST_SCHEMA:
        report.error("MANIFEST_SCHEMA", f"expected $schema = {MANIFEST_SCHEMA}")
    name = obj.get("name")
    if not isinstance(name, str) or not PLUGIN_NAME.fullmatch(name) or SINGLE_DOT_DASH.search(name):
        report.error("MANIFEST_NAME", "invalid plugin name per Agent Plugins v1")
        name = None
    else:
        if len(name) > 64:
            report.error("MANIFEST_NAME", "plugin name too long")
    for field in sorted(PORTABLE_FORBIDDEN & obj.keys()):
        report.error("MANIFEST_PORTABLE_MISUSE",
                     f"'{field}' is not a portable top-level plugin.json component declaration")
    extra = obj.keys() - VALID_MANIFEST_FIELDS
    for field in sorted(extra - PORTABLE_FORBIDDEN):
        report.warn("MANIFEST_UNKNOWN_FIELD",
                    f"'{field}' is not standard; v1 clients ignore unknown top-level fields")
    report.note("MANIFEST", f"found plugin identity '{name or '(invalid)'}'")
    return name


def frontmatter_name(path: Path, report: Report) -> str | None:
    try:
        body = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        report.error("HARNESS_SKILL_UNREADABLE", f"{path}: {exc}")
        return None
    match = FRONTMATTER.match(body)
    if not match:
        report.error("HARNESS_SKILL_FRONTMATTER", f"{path}: no YAML frontmatter")
        return None
    names = re.findall(r"^name:[ \t]*[\"']?([^\s\"'#]+)", match.group(1), re.M)
    if len(names) != 1:
        report.error("HARNESS_SKILL_NAME", f"{path}: expected one 'name:' field")
        return None
    return names[0]


def check_skills(root: Path, name: str | None, report: Report) -> None:
    skills = root / "skills"
    if skills.exists() and not skills.is_dir():
        report.error("SKILLS_PATH", "skills/ exists but is not a directory")
        return
    if not skills.is_dir():
        report.note("HARNESS_OPTIONAL", "no skills/; no Harness required")
        if (root / "scripts/harness.py").exists():
            report.error("ORPHAN_HARNESS", "scripts/harness.py exists without a discoverable Harness Skill")
        return
    harnesses = sorted(
        child for child in skills.iterdir() if child.is_dir() and child.name.endswith("-harness")
    )
    if len(harnesses) > 1:
        report.error("MULTIPLE_HARNESSES",
                     f"expected zero or one optional Harness Skill, found: "
                     f"{', '.join(h.name for h in harnesses)}")
    if not harnesses:
        report.note("HARNESS_OPTIONAL", "zero Harness Skills is valid")
    for h in harnesses:
        skill_file = h / "SKILL.md"
        if not skill_file.is_file():
            report.error("HARNESS_NOT_DISCOVERABLE", f"{skill_file}: not an Agent Skill entry")
            continue
        declared = frontmatter_name(skill_file, report)
        if declared != h.name or not SKILL_NAME.fullmatch(h.name):
            report.error("HARNESS_SKILL_NAME",
                         f"{h.name}: SKILL.md name {declared!r} must match the skill directory")
        if name and h.name != f"{name}-harness":
            report.warn("HARNESS_NAME_MIGRATION",
                        f"{h.name}: recommended canonical name is '{name}-harness'; "
                        "migrate compatibly, not by breaking installed clients")
        report.note("HARNESS_PRESENT", f"discoverable optional Harness: skills/{h.name}/SKILL.md")
    if (root / "scripts/harness.py").exists() and not harnesses:
        report.error("ORPHAN_HARNESS",
                     "root scripts/harness.py is not tied to a discoverable *-harness Skill")
    if (root / "src/harness").is_dir():
        report.warn("PRIVATE_HARNESS_REVIEW",
                    "legacy src/harness exists: document actual entry/owner; "
                    "not proof of dead code or a failure by itself")


def check_mcp(root: Path, report: Report) -> None:
    path = root / "mcp.json"
    if not path.exists():
        report.note("MCP_OPTIONAL", "mcp.json absent; that is valid")
        return
    if not path.is_file():
        report.error("MCP_FILE", "mcp.json exists but is not a file")
        return
    obj = read_json(path, report)
    if not isinstance(obj, dict):
        report.error("MCP_OBJECT", "mcp.json must be a JSON object")
        return
    if obj.get("$schema") != MCP_SCHEMA:
        report.error("MCP_SCHEMA", f"expected $schema = {MCP_SCHEMA}")
    if set(obj) != {"$schema", "mcpServers"}:
        report.error("MCP_TOP_LEVEL", "mcp.json supports only $schema and mcpServers")
    servers = obj.get("mcpServers")
    if not isinstance(servers, dict):
        report.error("MCP_SERVERS", "mcpServers must be an object")
        return
    for server_id, cfg in servers.items():
        if not isinstance(server_id, str) or not server_id or not isinstance(cfg, dict):
            report.error("MCP_ENTRY", f"bad server entry {server_id!r}")
            continue
        typ = cfg.get("type")
        if typ == "stdio":
            cmd = cfg.get("command")
            if not isinstance(cmd, str) or not cmd or any(ch.isspace() for ch in cmd):
                report.error("MCP_STDIO_COMMAND",
                             f"{server_id}: command must be a single executable token")
            elif "/" in cmd and not cmd.startswith("./"):
                report.error("MCP_STDIO_PATH",
                             f"{server_id}: packaged commands require ./-relative paths")
            cwd = cfg.get("cwd")
            if cwd is not None and (not isinstance(cwd, str) or not (
                cwd.startswith("./") or cwd == "${PLUGIN_ROOT}" or
                cwd.startswith("${PLUGIN_ROOT}/") or cwd == "${PLUGIN_DATA}" or
                cwd.startswith("${PLUGIN_DATA}/")
            )):
                report.error("MCP_STDIO_CWD", f"{server_id}: invalid portable cwd")
        elif typ in ("streamable-http", "sse"):
            url = cfg.get("url")
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                report.error("MCP_REMOTE_URL", f"{server_id}: invalid http(s) URL")
        else:
            report.error("MCP_TYPE", f"{server_id}: unsupported MCP server type {typ!r}")
    report.note("MCP", f"validated minimal MCP config for {len(servers)} server(s)")


def check_agents(root: Path, report: Report) -> None:
    path = root / "AGENTS.md"
    if not path.is_file():
        report.error("AGENTS_REQUIRED", "AGENTS.md must refer to organization architecture policy")
        return
    try:
        contents = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        report.error("AGENTS_UNREADABLE", str(exc))
        return
    if POLICY_TOKEN not in contents or POLICY_URL not in contents:
        report.error("POLICY_LINK_REQUIRED", f"AGENTS.md must link to {POLICY_URL}")


def check(root: Path) -> Report:
    report = Report()
    check_agents(root, report)
    name = check_manifest(root, report)
    check_skills(root, name, report)
    check_mcp(root, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Partme Agent Plugin Architecture Policy v1")
    parser.add_argument("--repo", type=Path, default=Path("."), help="plugin repository checkout")
    args = parser.parse_args()
    root = args.repo.resolve()
    if not root.is_dir():
        parser.error(f"repository directory missing: {root}")
    report = check(root)
    report.print()
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
