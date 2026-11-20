# Standing Instructions

## Project
* **tess-utils:** shared converters for the Tesserae projects (`tess-shell`, Tesserae UI): the value forms a TDL file writes (colour, four-sided values, corner radii, enum words, image bytes) turned into the one form tre takes (ADR-0017 and ADR-0018 in the design vault). Import name `tess_utils`, repo `mindderivative/tess-utils` (public, MIT, copyright "Mind Derivative"), version in `src/tess_utils/__init__.py` (0.2.2 is the latest release, tag `v0.2.2`). Versioning (user, 2026-11-15): while 0.2.x, a change takes the next patch number; a released version is never reused.
* **Distribution:** two routes. (1) PyPI as `tesserae-utils` (import stays `tess_utils`), published by `.github/workflows/release.yml` with Trusted Publishing (owner `mindderivative`, repository `tess-utils`, workflow `release.yml`, environment `pypi`) on a `vX.Y.Z` tag; the `pypi` environment's approval for each release is the user's. (2) The compiled route the consumers use: one `.so` (`mypyc`) plus a type stub and a stamp (`tools/build_so.py`, output in `build/so/`, ignored by git), carried in each consumer's `_vendor/` after a SHA-256 check (`vendor.json` is the manifest the consumer's sync script reads); the release workflow attaches it to the GitHub release.
* **Rule for adding a function** (`README.md`, "What belongs here"): at least two projects use it, it is a few lines of our own code (a library only for work that would be a project of its own, ADR-0019), it imports no Tesserae package, it has no dependency and no UI or schema meaning, and it has tests. Schema, typing and UI meaning stay in the consumers.
* **Imports:** modules import only the standard library; Pillow only inside `decode_image`'s function (`tests/test_no_imports.py` enforces both). Nothing imports `tess_re`, `tess_el`, `tess_dl`, `tess_ui` or `tess_shell`.
* **Source and `.so` must behave alike:** the public functions take `object` and validate, so a wrong type is a `ValueError` and never a `TypeError` (mypyc would raise one). `uv run python tools/build_so.py --test` runs the suite against the compiled file.
* **Decided:** Python `>=3.14`, hatchling, `src/` layout, no runtime dependencies (Pillow is the optional extra `image`). A new converter, a change to what a function accepts, a new dependency, a version bump, a tag, a release file and anything that publishes wait for the user. Consumers vendor a tagged copy: a change here that alters a result is a change in every consumer, so say so in `CHANGELOG.md`.

## Environment
* **venv:** `~/Projects/pyDev/pyEnvs/tess-utils` (Python 3.14.9, uv-made, no pip), set up with the project installed in editable mode and the `dev` and `docs` groups. `.vscode/settings.json` points the editor at `~/Projects/pyDev/pyEnvs/tess-utils/bin/python`. Recreate or refresh it with `UV_PROJECT_ENVIRONMENT=~/Projects/pyDev/pyEnvs/tess-utils uv sync --group docs`. `[tool.uv]` keeps `python-preference = "only-system"` (the system CPython with the GIL).
* **Checks**, all from that venv's `bin/` (or `uv run` with the variable above): `pytest -q` (197 tests, under a second), `ruff check src tests tools`, `ruff format --check src tests tools` (Python only: ruff's Markdown formatting would rewrite the README's code block), `mypy` (strict, `src` only). The suite is headless and quick: run it whole before calling work done.
* **Docs:** `mkdocs build --strict` from that venv (config `mkdocs.yml`, pages in `docs/`); the site goes to `site/` (ignored). `docs/changelog.md` is a generated copy of `CHANGELOG.md`: after editing the changelog run `python3 tools/sync_changelog.py` (CI fails with `--check` if they differ).
* **CI/CD** (`.github/workflows/`, actions pinned by SHA): `ci.yml` (test, lint and types, wheel smoke test, mypyc build with the suite run against it, docs build, aggregate `CI result` job required by branch protection), `docs.yml` (Pages deploy from `main`), `release.yml` (on a `vX.Y.Z` tag: checks, wheel and sdist, the compiled file, the `pypi` environment's approval, PyPI, then a GitHub release carrying the wheel, sdist, compiled file, stub and stamp), `dependabot.yml`. Check a workflow edit with `actionlint .github/workflows/*.yml` and `~/.claude/skills/gh-cicd/scripts/check-pins.sh .github/workflows`. Approving each release in the `pypi` environment is the user's.

## Skills, tools and hooks
* **Session start:** run `tools/status.sh` (branch, unpushed work, version, graph), then read the memory entity for this project.
* **Tools:** `tools/build_so.py` builds the release files; `tools/status.sh`; `tools/graphify_agents.py` and `tools/graphify_refresh.sh` (below).
* **Hooks** (`.claude/hooks/`, registered in `.claude/settings.json`): `bash_guard.sh` blocks `uv publish`, `twine upload` and `gh release create`, and lints staged Python before a commit; `ruff_edit.sh` and `tests_after_edit.sh` run after each edit under `src/`, `tests/` or `tools/`. Both use the venv above.
* **Graphify:** `graphify-out/` is a local code graph (ignored by git). A `Stop` hook (`tools/graphify_refresh.sh`) rebuilds it when a `.py` or docs file changed. Do not run `graphify claude install`; after upgrading graphify run `python3 tools/graphify_agents.py`, which keeps the `## graphify` section below and the PreToolUse hooks current.

## Documentation Policy
* **IMPORTANT:** update `README.md`, `CHANGELOG.md` and `docs/` as soon as a step, stage or feature is finished. A function's docstring is the source for `docs/reference.md`: change both together.
* Design decisions are written in this repository, not left in the vault; the vault notes (`tess-utils Brief`, ADR-0017) are the history.

## Commit Policy
* **YOU MUST** commit locally and automatically as soon as a step, stage or feature is finished. Match the existing commit style (`git log`): a short imperative subject, then a body when it helps. Do not wait for a `/commit` command.
* **Staging:** stage an explicit file list. Never `git add -A` or `git add .`.
* **Push and PR:** push to a branch `feat/<id>` or `fix/<id>` and open a PR (against `main`, or against another base branch when the task says so); `main` is protected (PR plus the `CI result` check), so never push to it and never force-push. Bots never merge. Without the user's explicit instruction, never: change the repository's visibility or settings, create or push a tag, create a release, publish to PyPI. The repository is public, so a push publishes: check the commits first; a `vX.Y.Z` tag starts the release workflow.

## Memory Policy
* **YOU MUST** update the memory MCP server when a local commit changes something worth remembering: a decision and its reason, a lesson, a standing instruction, or the project's status. Do not log each commit; git history already holds that.
* Keep one compact entity for the project (`tess-utils`), update it in place, and prune stale entries (back up the graph before pruning).

## Agent instructions
* They live in `AGENTS.md`; `CLAUDE.md` only imports it (`@AGENTS.md`). If a tool adds a section to `CLAUDE.md`, move it here.
* `.claude/settings.local.json` holds machine-specific hooks and is not committed (the global git ignore covers it).

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
