"""Shared converters for the Tesserae projects (tess-utils Brief, ADR-0017).

Pure functions that turn the value forms a TDL file writes into the single form tre takes. Nothing
here imports ``tess_re``, ``tess_el``, ``tess_dl``, ``tess_ui`` or ``tess_shell``, and the 0.1
modules import nothing outside the standard library.
"""

from __future__ import annotations

from tess_utils.color import parse_color
from tess_utils.enums import to_tre_word
from tess_utils.radius import expand_radius
from tess_utils.sides import expand_sides, to_tre_order

__version__ = "0.1.1"

__all__ = [
    "__version__",
    "expand_radius",
    "expand_sides",
    "parse_color",
    "to_tre_order",
    "to_tre_word",
]
