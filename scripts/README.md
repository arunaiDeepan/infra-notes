# Obsidian ↔ GitHub Markdown Bridge

Keeps the **working tree in Obsidian wikilink form** (`[Heading](#heading)`, `[File](File.md)`) while the **repo / GitHub sees standard markdown anchor links** (`[text](#slug)`, `[text](File.md)`).

```
edit (Obsidian)         git add              git commit             git pull / checkout
       │                    │                      │                       │
       ▼                    ▼                      ▼                       ▼
   wikilinks  ──clean──►  anchors  ──hook (no-op)──►  anchors  ──smudge──►  wikilinks
   (working)              (index)                   (commit/remote)        (working)
```

---

## Quick start

After cloning this repo, run once:

```sh
bash scripts/install.sh
```

That's it. Edit notes normally; everything else is automatic.

---

## Daily workflow

| What you do                           | What happens                                                                                |
| :------------------------------------ | :------------------------------------------------------------------------------------------ |
| Edit `.md` files with `[wikilinks](wikilinks.md)` | Working tree always shows wikilinks.                                                        |
| `git add file.md`                     | **Clean filter** converts → anchors in the index.                                           |
| `git commit`                          | **Pre-commit hook** runs the same conversion as a safety net (no-op if filter already ran). |
| `git push`                            | GitHub renders anchor links correctly.                                                      |
| `git pull` / `git checkout`           | **Smudge filter** converts back → wikilinks in your working tree.                           |
| `git status` shows `AM` flag          | Normal - staged (anchors) intentionally differs from working (wikilinks).                   |

Override / escape hatches:

| Command                                                                      | Effect                                                                            |
| :--------------------------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| `SKIP_OBSIDIAN_CONVERT=1 git commit -m "…"`                                  | Bypass the pre-commit hook for one commit. (Filter still runs at `git add` time.) |
| `git -c filter.obsidian.clean=cat -c filter.obsidian.smudge=cat add file.md` | Bypass both filters for one command.                                              |
| `python scripts/obsidian_to_github.py file.md`                               | Manual in-place forward conversion.                                               |
| `python scripts/github_to_obsidian.py file.md`                               | Manual in-place reverse conversion.                                               |
| `python scripts/obsidian_to_github.py --check file.md`                       | Exit 1 if file has wikilinks (useful in CI).                                      |

---

## The scripts

### `obsidian_to_github.py` - forward (wikilinks → anchors)

Used as the clean filter and as the pre-commit hook's transform. Also runnable manually.

```sh
cat file.md | python scripts/obsidian_to_github.py            # stdin → stdout
python scripts/obsidian_to_github.py file.md                  # in-place
python scripts/obsidian_to_github.py --check file.md          # exit 1 if would change
python scripts/obsidian_to_github.py --source-path notes/x.md # set source for relative paths
```

What it converts:

| Input                     | Output                           |
| :------------------------ | :------------------------------- |
| `[Heading](#heading)`            | `[Heading](#slug)`               |
| `[Alias](#heading)`     | `[Alias](#slug)`                 |
| `[File](File.md)`                | `[File](File.md)`                |
| `[Alias](File.md)`         | `[Alias](File.md)`               |
| `[File > Heading](File.md#heading)`        | `[File > Heading](File.md#slug)` |
| `[Alias](File.md#heading)` | `[Alias](File.md#slug)`          |

Slug rules match GitHub's `jch/html-pipeline`: lowercase, strip everything that isn't a word char / hyphen / space, then replace spaces with hyphens (consecutive spaces become consecutive hyphens - so `-` produces `--`).

### `github_to_obsidian.py` - reverse (anchors → wikilinks)

Used as the smudge filter. Inverse of the above.

```sh
cat file.md | python scripts/github_to_obsidian.py            # stdin → stdout
python scripts/github_to_obsidian.py file.md                  # in-place
python scripts/github_to_obsidian.py --check file.md          # exit 1 if would change
```

Detection rules (leaves links alone otherwise):

- URL starts with `#` → same-file anchor. Looks up the slug in headings of the current file.
- URL is a relative `.md` path (URL-decoded) with optional `#anchor` → cross-file link. Looks up the file by basename in the repo, then the slug in that file's headings.
- URL starts with `http://`, `https://`, `mailto:`, `ftp(s)://`, `//` → external, untouched.

When the slug can't be resolved (heading removed, file missing), the link is left in markdown form rather than mangled.

### `install.sh` - per-clone setup

Idempotent. Configures `core.hooksPath` and the `filter.obsidian.*` git config for this repo. Run after every fresh clone. Re-running is safe.

### `../.githooks/pre-commit` - belt-and-suspenders

Backup converter for when someone forgot to run `install.sh`. Manipulates the staged blob via `git update-index --cacheinfo` (the working tree is never touched). Skip with `SKIP_OBSIDIAN_CONVERT=1`.

### `../.gitattributes` - declares the filter

```
*.md filter=obsidian
```

Tracked. Without the matching `filter.obsidian.clean/smudge` git-config entries (set by `install.sh`), it's a no-op.

---

## How it works (three layers)

| Layer               | Trigger                                                        | Direction                            | Purpose                                                                                                                        |
| :------------------ | :------------------------------------------------------------- | :----------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **Clean filter**    | `git add` (any time the working tree → index)                  | wikilinks → anchors                  | Primary forward conversion.                                                                                                    |
| **Smudge filter**   | `git checkout`, `git pull`, `git clone` (index → working tree) | anchors → wikilinks                  | Primary reverse conversion. Keeps the working tree Obsidian-friendly forever.                                                  |
| **Pre-commit hook** | `git commit`                                                   | wikilinks → anchors (on staged blob) | Fallback when filters aren't configured (e.g. someone skipped `install.sh`). Idempotent: no-op if blob is already anchor-form. |

`filter.obsidian.required = false` so that if Python is missing the filter passes content through unchanged instead of breaking every checkout. The resulting working tree just has anchor links - still valid markdown, still works in Obsidian.

---

## Reusing this in another repo

Three things travel with the repo (commit them):

```
.gitattributes
.githooks/pre-commit
scripts/
├── obsidian_to_github.py
├── github_to_obsidian.py
├── install.sh
└── README.md
```

In the target repo:

```sh
# Copy the four tracked items in.
cp -r /path/to/this/repo/.gitattributes  .
cp -r /path/to/this/repo/.githooks       .
cp -r /path/to/this/repo/scripts         .

git add .gitattributes .githooks scripts
git commit -m "Add obsidian↔github markdown bridge"

# Per-clone activation (every collaborator runs this once):
bash scripts/install.sh
```

No edits to the scripts are needed - they pick up the repo root via `git rev-parse --show-toplevel` and walk it for cross-file resolution.

---

## Troubleshooting

| Symptom                                                          | Likely cause                                                                    | Fix                                                                                                        |
| :--------------------------------------------------------------- | :------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------- |
| Working tree has `[text](#slug)` instead of `[Heading](#heading)`       | Forgot per-clone install OR python missing                                      | Run `bash scripts/install.sh`, then `git rm --cached -r -- '*.md' && git checkout -- '*.md'` to re-smudge. |
| `git status` shows `AM` on every .md file                        | Working tree (wikilinks) differs from index (anchors) - **this is by design**   | Nothing to fix; commit normally.                                                                           |
| Hook says "converted wikilinks" but you didn't edit              | First commit after install, or filter wasn't configured at `git add` time       | Expected and idempotent - subsequent commits are silent.                                                   |
| Pre-commit hook does nothing                                     | `core.hooksPath` not set                                                        | Re-run `bash scripts/install.sh`.                                                                          |
| Conversion fails with `python: not found`                        | Python missing from PATH                                                        | Install Python 3.8+. With `required = false`, current files pass through unchanged.                        |
| New heading in TOC link doesn't resolve in the reverse direction | Headings differ between two files with the same slug                            | Rename one heading so slugs are unique.                                                                    |
| Round-trip changed unrelated content                             | A "markdown link" in the source happened to match `[text](File.md#anchor)` form | Wrap the literal text in code fences/backticks to avoid the regex.                                         |

---

## Caveats

- **Not lossless for hand-written markdown links.** The reverse converter assumes every `[text](File.md)` was originally a wikilink. If you write a literal markdown link, it'll be converted to a wikilink on the next checkout. Wrap such literals in inline code or HTML to protect them.
- **Slug collisions** (two headings with the same slug in one file) - first match wins, second is unrecoverable in reverse. GitHub itself disambiguates with `-1`, `-2`; this bridge doesn't.
- **`required = false` means silent passthrough.** If your Python install is broken, you get unconverted files instead of an error. Set to `true` in `.git/config` if you'd rather fail loudly.
- **No CRLF surprise:** both converters use binary stdin/stdout so they don't accidentally rewrite line endings on Windows.

> To format all md files - `npx prettier --write "**/*.md"`
