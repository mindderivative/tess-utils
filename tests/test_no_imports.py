"""Modules import nothing outside the standard library and nothing of Tesserae at import time.

The one exception is ``image.py``, which imports Pillow lazily inside ``decode_image``.
"""

import ast
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "tess_utils"
FORBIDDEN = {"tess_re", "tess_el", "tess_dl", "tess_ui", "tess_shell"}


def _imports(nodes: list[ast.AST]) -> set[str]:
    found: set[str] = set()
    for tree in nodes:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return found


def test_module_level_imports_are_standard_library_or_this_package() -> None:
    for path in SRC.glob("*.py"):
        tree = ast.parse(path.read_text())
        found = _imports([n for n in tree.body if isinstance(n, ast.Import | ast.ImportFrom)])
        outside = {n for n in found if n not in sys.stdlib_module_names and n != "tess_utils"}
        assert outside == set(), path.name


def test_only_the_image_module_imports_pillow_and_only_inside_a_function() -> None:
    for path in SRC.glob("*.py"):
        found = _imports([ast.parse(path.read_text())])
        assert not found & FORBIDDEN, path.name
        outside = {n for n in found if n not in sys.stdlib_module_names and n != "tess_utils"}
        assert outside == ({"PIL"} if path.name == "image.py" else set()), path.name
