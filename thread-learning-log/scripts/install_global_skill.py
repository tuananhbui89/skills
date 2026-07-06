#!/usr/bin/env python3
"""Install this skill into ~/.codex/skills and patch writable roots."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex home directory. Defaults to ~/.codex.",
    )
    parser.add_argument(
        "--writable-root",
        "--workspace-root",
        dest="writable_root",
        type=Path,
        default=None,
        help=(
            "Writable root to add to Codex config. Defaults to the installed "
            "thread-learning-log skill directory."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without writing files.",
    )
    return parser.parse_args()


def render_array_line(key: str, values: list[str]) -> str:
    rendered_values = ", ".join(json.dumps(value) for value in values)
    return f"{key} = [{rendered_values}]"


def parse_array_assignment(lines: list[str], start_index: int, key: str) -> tuple[list[str], int]:
    line = lines[start_index]
    rhs = line.split("=", 1)[1].strip()
    collected = [rhs]
    end_index = start_index

    while True:
        candidate = "\n".join(collected)
        try:
            values = ast.literal_eval(candidate)
        except Exception:  # noqa: BLE001
            end_index += 1
            if end_index >= len(lines):
                raise ValueError(f"could not parse {key}: unexpected EOF while parsing")
            collected.append(lines[end_index].strip())
            continue

        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise ValueError(f"{key} must be a list of strings")
        return values, end_index


def update_or_add_array_line(lines: list[str], key: str, new_value: str) -> list[str]:
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith(f"{key} ="):
            continue
        values, end_index = parse_array_assignment(lines, index, key)
        if new_value not in values:
            values.append(new_value)
        updated_lines = list(lines)
        updated_lines[index : end_index + 1] = [render_array_line(key, values)]
        return updated_lines

    section_header = "[sandbox_workspace_write]"
    insert_at = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == section_header:
            insert_at = index + 1
            while insert_at < len(lines) and not lines[insert_at].strip().startswith("["):
                insert_at += 1
            break

    if insert_at is None:
        insert_at = next(
            (index for index, line in enumerate(lines) if line.strip().startswith("[")),
            len(lines),
        )

    new_line = render_array_line(key, [new_value])
    updated_lines = list(lines)
    updated_lines.insert(insert_at, new_line)
    return updated_lines


def patch_config(config_path: Path, writable_root: Path, dry_run: bool) -> None:
    if not config_path.exists():
        raise FileNotFoundError(f"config not found: {config_path}")

    original_text = config_path.read_text(encoding="utf-8")
    lines = original_text.splitlines()
    for key in ("writable_roots", "extra_writable_roots"):
        lines = update_or_add_array_line(lines, key, str(writable_root))
    updated_text = "\n".join(lines).rstrip() + "\n"

    if dry_run:
        sys.stdout.write(f"Would patch {config_path}\n")
        return

    config_path.write_text(updated_text, encoding="utf-8")


def copy_skill(skill_dir: Path, target_dir: Path, dry_run: bool) -> None:
    if dry_run:
        sys.stdout.write(f"Would copy {skill_dir} -> {target_dir}\n")
        return
    shutil.copytree(
        skill_dir,
        target_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def main() -> int:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    codex_home = args.codex_home
    target_skill_dir = codex_home / "skills" / skill_dir.name
    config_path = codex_home / "config.toml"
    writable_root = args.writable_root or target_skill_dir

    try:
        if not codex_home.exists():
            raise FileNotFoundError(f"Codex home does not exist: {codex_home}")

        if args.dry_run:
            sys.stdout.write(f"Skill source: {skill_dir}\n")
            sys.stdout.write(f"Target skill dir: {target_skill_dir}\n")
            sys.stdout.write(f"Writable root: {writable_root}\n")

        copy_skill(skill_dir, target_skill_dir, args.dry_run)
        patch_config(config_path, writable_root, args.dry_run)
        if args.dry_run:
            sys.stdout.write("Dry run complete.\n")
        else:
            sys.stdout.write(
                f'Installed skill="{skill_dir.name}" codex_home="{codex_home}"\n'
            )
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
