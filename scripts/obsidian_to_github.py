#!/usr/bin/env python3
"""Convert Obsidian wikilinks to GitHub-flavored markdown links.

Transforms:
  [[#Heading]]              -> [Heading](#github-slug)
  [[#Heading|Alias]]        -> [Alias](#github-slug)
  [[File]]                  -> [File](File.md)
  [[File|Alias]]            -> [Alias](File.md)
  [[File#Heading]]          -> [File > Heading](File.md#github-slug)
  [[File#Heading|Alias]]    -> [Alias](File.md#github-slug)

For cross-file links, the script walks the repo to find the .md file
and emits a relative path from the source file.

Usage:
  cat file.md | obsidian_to_github.py                # stdin -> stdout
  obsidian_to_github.py file.md                      # in-place rewrite
  obsidian_to_github.py --source-path notes/foo.md   # set source for relative paths
"""

import argparse
import os
import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")


def slugify(text: str) -> str:
    """Replicate GitHub's heading-anchor slug rules.

    Algorithm (matches github.com/jch/html-pipeline TableOfContentsFilter):
      1. lowercase
      2. strip everything that isn't a unicode word char, hyphen, or space
      3. replace each single space with a single hyphen (consecutive spaces are
         preserved as consecutive hyphens — e.g. " — " becomes "--")
    """
    text = text.lower()
    text = re.sub(r"[^\w\- ]+", "", text, flags=re.UNICODE)
    text = text.replace(" ", "-")
    return text


def find_repo_md_files(repo_root: Path) -> dict[str, Path]:
    """Return {basename_without_ext: absolute_path} for every .md in repo."""
    index: dict[str, Path] = {}
    for p in repo_root.rglob("*.md"):
        if ".git" in p.parts:
            continue
        index.setdefault(p.stem, p)
    return index


def url_encode_path(path: str) -> str:
    return urllib.parse.quote(path, safe="/")


def make_converter(source_file: Path | None, repo_root: Path | None):
    md_index: dict[str, Path] = {}
    if repo_root is not None:
        md_index = find_repo_md_files(repo_root)

    def resolve_file_link(file_part: str) -> str:
        target = md_index.get(file_part)
        if target is None:
            return url_encode_path(file_part + ".md")
        if source_file is None:
            return url_encode_path(target.name)
        try:
            rel = os.path.relpath(target, start=source_file.parent).replace(os.sep, "/")
        except ValueError:
            rel = target.name
        return url_encode_path(rel)

    def convert(match: re.Match) -> str:
        inner = match.group(1).strip()

        if "|" in inner:
            target, alias = inner.split("|", 1)
            target, alias = target.strip(), alias.strip()
        else:
            target, alias = inner, None

        if "#" in target:
            file_part, heading = target.split("#", 1)
            file_part, heading = file_part.strip(), heading.strip()
        else:
            file_part, heading = target, None

        # Same-file heading link: [[#Heading]] or [[#Heading|Alias]]
        if not file_part:
            slug = slugify(heading or "")
            display = alias if alias else heading
            return f"[{display}](#{slug})"

        # Cross-file with heading: [[File#Heading]] / [[File#Heading|Alias]]
        if heading:
            path = resolve_file_link(file_part)
            slug = slugify(heading)
            display = alias if alias else f"{file_part} > {heading}"
            return f"[{display}]({path}#{slug})"

        # File only: [[File]] / [[File|Alias]]
        path = resolve_file_link(file_part)
        display = alias if alias else file_part
        return f"[{display}]({path})"

    return convert


def convert_text(text: str, source_file: Path | None = None, repo_root: Path | None = None) -> str:
    converter = make_converter(source_file, repo_root)
    return WIKILINK_RE.sub(converter, text)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?", help="File to rewrite in place (defaults to stdin->stdout)")
    ap.add_argument("--source-path", help="Source path used to compute relative links (when reading stdin)")
    ap.add_argument("--repo-root", help="Repo root for cross-file resolution (defaults to git toplevel or CWD)")
    ap.add_argument("--check", action="store_true", help="Exit non-zero if conversion would change content (no write)")
    args = ap.parse_args(argv)

    repo_root: Path
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        import subprocess
        try:
            top = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            repo_root = Path(top)
        except Exception:
            repo_root = Path.cwd()

    source_file: Path | None = None
    if args.file:
        source_file = Path(args.file).resolve()
        # Read as bytes to avoid any newline translation, then decode UTF-8.
        original = source_file.read_bytes().decode("utf-8")
    else:
        source_file = Path(args.source_path).resolve() if args.source_path else None
        # On Windows, sys.stdin in text mode translates CRLF/LF — use buffer for byte-faithful I/O.
        original = sys.stdin.buffer.read().decode("utf-8")

    converted = convert_text(original, source_file=source_file, repo_root=repo_root)

    if args.check:
        return 0 if converted == original else 1

    if args.file:
        if converted != original:
            source_file.write_bytes(converted.encode("utf-8"))
    else:
        sys.stdout.buffer.write(converted.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
