# Distribution

`tess-utils` is not released on PyPI (maintainer's decision, 2026-11-08; the source repository
became public on 2026-11-15 and the decision stands). The package metadata carries the classifier
`Private :: Do Not Upload`.

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

A tag (`vX.Y.Z`) and a release file are the maintainer's to make.
