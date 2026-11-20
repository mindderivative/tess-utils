"""Corner radii, in the form tre takes."""

from __future__ import annotations

import math
import os
from collections.abc import Sequence

Radii = tuple[float, float, float, float]


def _radius(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"a radius is a number, not {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"a radius is not finite: {value!r}")
    if value < 0:
        raise ValueError(f"a radius cannot be negative: {value!r}")
    return float(value)


def expand_radius(value: object) -> Radii:
    """One number (every corner) or four numbers from the top-left corner clockwise, to
    ``(top_left, top_right, bottom_right, bottom_left)``, the form tre takes. A radius is never
    negative; a list of other than four numbers is an error."""
    if isinstance(value, str):
        raise ValueError(f"a radius is a number, not text: {value!r}")
    if isinstance(value, Sequence):
        if len(value) != 4:
            raise ValueError(
                "a list of radii has four numbers from the top-left corner clockwise, "
                f"not {len(value)}"
            )
        top_left, top_right, bottom_right, bottom_left = (_radius(v) for v in value)
        return (top_left, top_right, bottom_right, bottom_left)
    one = _radius(value)
    return (one, one, one, one)
