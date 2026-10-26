#!/usr/bin/env python3
"""Generate the supported-TV table in README.md from examples/*/tv.json.

Usage:
    python tools/gen_tables.py
    python tools/gen_tables.py --check

Only selected Xiaomi and TCL Android TV / Google TV profiles are accepted.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from catalog import SUPPORTED_BRANDS, is_supported_profile


KEYS = ("tv", "os", "brand", "notes")
OPTIONAL = ("readme_os",)
WIDTH = 120
README_HEADER = ["| TV | OS |", "|---|---|"]


class Problem(Exception):
    """A profile or README marker is invalid."""


def folders(root: Path) -> list[Path]:
    return sorted(path for path in (root / "examples").iterdir() if path.is_dir())


def check_cell(where: str, key: str, value: object) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f'{where}: "{key}" must be a non-empty string']
    if value != value.strip() or "\n" in value:
        return [f'{where}: "{key}" must be one line with no space at either end']
    if re.search(r"(?<!\\)\|", value):
        return [f'{where}: "{key}" has a | that would split the table cell; write \\| instead']
    return []


def load(root: Path) -> list[tuple[str, dict]]:
    """Read and validate the selected Android/Google TV profiles."""
    problems: list[str] = []
    entries: list[tuple[str, dict]] = []
    for folder in folders(root):
        path = folder / "tv.json"
        where = f"examples/{folder.name}/tv.json"
        if not path.is_file():
            problems.append(f"{where} is missing")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"{where}: not valid JSON ({exc})")
            continue
        if not isinstance(data, dict):
            problems.append(f"{where}: must be a JSON object")
            continue
        unknown = sorted(set(data) - set(KEYS) - set(OPTIONAL))
        if unknown:
            problems.append(f"{where}: unknown key(s) {unknown}")
        for key in KEYS:
            problems += check_cell(where, key, data.get(key))
        if "readme_os" in data:
            problems += check_cell(where, "readme_os", data["readme_os"])
        if not is_supported_profile(data):
            problems.append(
                f"{where}: profile is outside this fork's scope: Xiaomi Mi/TV Box or Android 14 TVs; "
                "TCL at 75 inches or with no stated diagonal"
            )
        entries.append((folder.name, data))
    if problems:
        raise Problem("\n".join(problems))
    return entries


def ordered(entries: list[tuple[str, dict]]) -> list[tuple[str, dict]]:
    return sorted(entries, key=lambda entry: (entry[1]["tv"].casefold(), entry[0]))


def readme_rows(entries: list[tuple[str, dict]]) -> list[str]:
    return README_HEADER + [
        f"| {data['tv']} | {data.get('readme_os', data['os'])} |"
        for _, data in ordered(entries)
    ]


def wrap(items: list[str]) -> list[str]:
    lines, current = [], ""
    for item in items:
        piece = item + " ·"
        if current and len(current) + len(piece) + 1 > WIDTH:
            lines.append(current)
            current = piece
        else:
            current = f"{current} {piece}" if current else piece
    return lines + ([current] if current else [])


def brand_lines(entries: list[tuple[str, dict]]) -> list[str]:
    counts: dict[str, int] = {}
    for _, data in entries:
        counts[data["brand"]] = counts.get(data["brand"], 0) + 1
    names = sorted(counts, key=lambda name: (-counts[name], name.casefold()))
    return wrap([f"**{name}** {counts[name]}" for name in names])


def between(text: str, name: str, body: list[str]) -> str:
    lines = text.split("\n")
    starts = [index for index, line in enumerate(lines) if line.startswith(f"<!-- {name}:start")]
    ends = [index for index, line in enumerate(lines) if line.strip() == f"<!-- {name}:end -->"]
    if len(starts) != 1 or len(ends) != 1 or starts[0] > ends[0]:
        raise Problem(f"README.md: needs one {name}:start marker before one {name}:end marker")
    return "\n".join(lines[:starts[0] + 1] + [""] + body + [""] + lines[ends[0]:])


def render(root: Path) -> str:
    readme = (root / "README.md").read_text(encoding="utf-8")
    entries = load(root)
    readme = between(readme, "tv-brands", brand_lines(entries))
    return between(readme, "tv-table", readme_rows(entries))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when README is stale")
    args = parser.parse_args(argv)
    if not args.root.is_dir() or not (args.root / "examples").is_dir() or not (args.root / "README.md").is_file():
        print("--root must point to this repository", file=sys.stderr)
        return 2
    try:
        text = render(args.root)
    except Problem as exc:
        print(exc, file=sys.stderr)
        return 2
    path = args.root / "README.md"
    if args.check:
        if path.read_text(encoding="utf-8") != text:
            print("Out of date: README.md. Run python tools/gen_tables.py.", file=sys.stderr)
            return 1
        return 0
    if path.read_text(encoding="utf-8") == text:
        print("Up to date.")
        return 0
    path.write_text(text, encoding="utf-8")
    print("Updated: README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
