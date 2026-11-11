"""Build the release files: one compiled ``tess_utils`` ``.so`` (maintainer, 2026-11-08), its
stub and its stamp.

    uv run python tools/build_so.py            # builds into build/so and prints the stamp
    uv run python tools/build_so.py --test     # ... and runs the test suite against the .so

``mypyc`` compiles several modules into one shared library plus a small shim ``.so`` per module,
which is not one file. A single module becomes a single file, so the independent 0.1 modules are
merged into one ``tess_utils.py`` first (``tess_utils.color`` and the like are not importable from
the compiled file; the public names of the package are). ``tess_utils.pyi`` is the type stub a
consumer's mypy reads beside the file. The stamp ``tess_utils.stamp.json`` records the version, the
Python tag, and the SHA-256 of the file and of the stub, which a consumer checks before it carries
them (``vendor.json`` names the files a consumer copies).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "tess_utils"
MODULES = ("color", "sides", "radius", "enums", "image")  # independent of one another
OUT = ROOT / "build" / "so"


def merged_source() -> str:
    """One module with the modules' code and the package's public names."""
    imports: set[str] = set()
    parts: list[str] = []
    for name in MODULES:
        text = (SRC / f"{name}.py").read_text()
        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, ast.Import | ast.ImportFrom):
                if isinstance(node, ast.ImportFrom) and node.module in ("__future__",):
                    continue
                if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                    "tess_utils"
                ):
                    raise SystemExit(f"{name}.py imports another tess_utils module: not mergeable")
                imports.add(ast.get_source_segment(text, node) or "")
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue  # the module docstring
            else:
                parts.append(ast.get_source_segment(text, node) or "")
    init = ast.parse((SRC / "__init__.py").read_text())
    version = next(
        node.value.value
        for node in init.body
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and any(isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets)
    )
    names = sorted(
        [
            "__version__",
            "decode_image",
            "expand_radius",
            "expand_sides",
            "parse_color",
            "to_tre_order",
            "to_tre_word",
        ]
    )
    header = '"""tess_utils: shared converters for the Tesserae projects (one compiled file)."""\n'
    body = "\n\n\n".join(parts)
    return (
        f"{header}\nfrom __future__ import annotations\n\n"
        + "\n".join(sorted(i for i in imports if i))
        + f"\n\n__version__ = {version!r}\n\n\n{body}\n\n\n__all__ = {names!r}\n"
    )


def build() -> Path:
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    work = OUT / "work"
    work.mkdir()
    (work / "tess_utils.py").write_text(merged_source())
    subprocess.run([sys.executable, "-m", "mypyc", "tess_utils.py"], cwd=work, check=True)
    built = sorted(work.glob("tess_utils.*.so"))
    extra = sorted(p.name for p in work.glob("*.so") if p not in built)
    if len(built) != 1 or extra:
        raise SystemExit(f"expected one .so, found {[p.name for p in built]} and {extra}")
    target = OUT / built[0].name
    shutil.copy2(built[0], target)
    subprocess.run(
        [
            sys.executable,
            "-c",
            "from mypy.stubgen import main; main()",
            "-q",
            "-o",
            str(work),
            str(work / "tess_utils.py"),
        ],
        check=True,
    )
    shutil.copy2(work / "tess_utils.pyi", OUT / "tess_utils.pyi")
    shutil.rmtree(work)
    return target


def stamp(so: Path) -> dict[str, object]:
    version = ast.literal_eval(
        next(
            line.split("=", 1)[1].strip()
            for line in (SRC / "__init__.py").read_text().splitlines()
            if line.startswith("__version__")
        )
    )
    stub = so.parent / "tess_utils.pyi"
    data = {
        "name": so.name,
        "version": version,
        "python": sysconfig.get_config_var("SOABI") or "",
        "platform": platform.machine(),
        "sha256": hashlib.sha256(so.read_bytes()).hexdigest(),
        "files": {
            so.name: hashlib.sha256(so.read_bytes()).hexdigest(),
            stub.name: hashlib.sha256(stub.read_bytes()).hexdigest(),
        },
    }
    (OUT / "tess_utils.stamp.json").write_text(json.dumps(data, indent=2) + "\n")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", action="store_true", help="run the tests against the built file")
    args = parser.parse_args()
    so = build()
    print(json.dumps(stamp(so), indent=2))
    if args.test:
        env = {"PYTHONPATH": str(OUT), "PATH": "/usr/bin:/bin"}
        import os

        env = {**os.environ, "PYTHONPATH": str(OUT)}
        code = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(ROOT / "tests")],
            env=env,
            cwd=OUT,
        ).returncode
        raise SystemExit(code)


if __name__ == "__main__":
    main()
