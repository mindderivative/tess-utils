"""The 0.1 modules import nothing outside the standard library, and nothing of Tesserae."""

import ast
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "tess_utils"
FORBIDDEN = {"tess_re", "tess_el", "tess_dl", "tess_ui", "tess_shell", "PIL"}


def test_every_import_is_standard_library_or_this_package() -> None:
    found: set[str] = set()
    for path in SRC.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    outside = {
        name for name in found if name not in sys.stdlib_module_names and name != "tess_utils"
    }
    assert outside == set()
    assert not found & FORBIDDEN
