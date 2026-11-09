"""Four-sided values (padding, margin, inset, thickness) and tre's order for them."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

Sides = tuple[float, float, float, float]

_NAMES = ("left", "top", "right", "bottom")


def _number(value: object, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{what} is a number, not {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"{what} is not finite: {value!r}")
    return float(value)


def expand_sides(value: object) -> Sides:
    """One number (every side), or four numbers, or named sides, to ``(left, top, right, bottom)``.

    A mapping names ``left``, ``top``, ``right`` and ``bottom`` in any case; a side it does not name
    is 0. A list of two or three numbers is an error (ADR-0014 D72), as is an unknown side name.
    A negative number is allowed: whether a side may be negative is the caller's rule. Anything
    else is a ``ValueError`` (the parameter is typed ``object`` so a compiled build behaves alike).
    """
    if isinstance(value, Mapping):
        found = {str(name).lower(): _number(v, f"side {name}") for name, v in value.items()}
        unknown = [name for name in found if name not in _NAMES]
        if unknown:
            raise ValueError(f"unknown side {unknown[0]!r}; the sides are {', '.join(_NAMES)}")
        left, top, right, bottom = (found.get(name, 0.0) for name in _NAMES)
        return (left, top, right, bottom)
    if isinstance(value, str):
        raise ValueError(f"sides are numbers, not text: {value!r}")
    if isinstance(value, Sequence):
        if len(value) != 4:
            raise ValueError(
                f"a list of sides has four numbers (left, top, right, bottom), not {len(value)}"
            )
        left, top, right, bottom = (_number(v, "a side") for v in value)
        return (left, top, right, bottom)
    one = _number(value, "a side")
    return (one, one, one, one)


def to_tre_order(sides: Sides) -> Sides:
    """``(left, top, right, bottom)`` to ``(top, right, bottom, left)``, the order tre's margins
    use."""
    left, top, right, bottom = sides
    return (top, right, bottom, left)
