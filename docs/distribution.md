# Distribution

`tess-utils` is published to PyPI as `tesserae-utils` (import name `tess_utils`) by
`.github/workflows/release.yml`: Trusted Publishing from this repository, workflow `release.yml`,
environment `pypi`, on a `vX.Y.Z` tag. The PyPI release is the source package (a wheel and an
sdist). Before this the project was private and distributed only as the compiled file below
(maintainer, 2026-11-08); the PyPI name was added by the maintainer on 2026-11-15 and the compiled
file stays the way the Tesserae consumers carry it.

A release is one compiled file, built with `mypyc`:

| File | What it is |
|---|---|
| `tess_utils.<soabi>.so` | The merged package, compiled for one Python tag and platform |
| `tess_utils.pyi` | The type stub a consumer's mypy reads beside the file |
| `tess_utils.stamp.json` | The version, the Python tag and platform, and the SHA-256 of the file and the stub |

`vendor.json` is the manifest a consumer's sync script reads: the package name, the repository,
the stamp file and the files to copy (`{soabi}` is the consumer's Python tag). The sync script
itself lives in each consumer: it downloads a release, checks the stamp's SHA-256, and carries the
files in the consumer's `_vendor/` folder.

## Building

```
UV_PROJECT_ENVIRONMENT=~/Projects/pyDev/pyEnvs/tess-utils uv sync --group docs
uv run python tools/build_so.py            # builds into build/so and prints the stamp
uv run python tools/build_so.py --test     # ... and runs the test suite against the .so
```

`mypyc` compiles several modules into one shared library plus a shim per module, which is not one
file, so `tools/build_so.py` first merges the independent modules (`color`, `sides`, `radius`,
`enums`, `image`) into one. `tess_utils.color` and the like are therefore not importable from the
compiled file; the package's public names are.

## Automation

`ci.yml` runs on every push to `main` and every pull request: the tests, lint and types, the wheel
in a clean environment, the compiled build with the suite run against it, and the docs build.
`release.yml` runs on a `vX.Y.Z` tag: the same checks, then the wheel and sdist go to PyPI (after
the `pypi` environment's approval) and a GitHub release carries the wheel, the sdist and the
compiled file with its stub and stamp. A tag and the approval are the maintainer's to make.
