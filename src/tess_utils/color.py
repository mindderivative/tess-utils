"""Colour: the written forms of TDL to tre's ``(r, g, b, a)`` of 0 to 255 integers."""

from __future__ import annotations

import re

Color = tuple[int, int, int, int]

_FUNCTION = re.compile(r"rgba?\(\s*([^)]*?)\s*\)", re.IGNORECASE)


def parse_color(text: object) -> Color:
    """Read a colour written as ``#RRGGBB``, ``#RRGGBBAA`` (alpha last), ``#RGB``, ``#RGBA``,
    ``rgb(r g b)`` or ``rgba(r g b a)`` (spaces or commas; red to blue 0 to 255, alpha 0.0 to 1.0)
    or ``transparent``. Returns tre's ``(r, g, b, a)``, each an integer 0 to 255.

    Raises :class:`ValueError` naming the bad part, also for a value that is not text. The
    parameter is typed ``object`` on purpose: a compiled build (mypyc) would raise ``TypeError`` for
    a wrongly typed argument, and the source and the compiled file must behave alike.
    """
    if not isinstance(text, str):
        raise ValueError(f"a colour is written as text, not {type(text).__name__}")
    written = text.strip()
    if written.lower() == "transparent":
        return (0, 0, 0, 0)
    if written.startswith("#"):
        return _hex(written, text)
    if match := _FUNCTION.fullmatch(written):
        return _function(match.group(1), text)
    raise ValueError(
        f"not a colour: {text!r}; write #RRGGBB, #RRGGBBAA, rgba(r g b a) or transparent"
    )


def _hex(written: str, text: str) -> Color:
    bad = next((c for c in written[1:] if c not in "0123456789abcdefABCDEF"), None)
    if bad is not None:
        raise ValueError(f"not a colour: {text!r}; {bad!r} is not a hex digit")
    digits = written[1:]
    if len(digits) not in (3, 4, 6, 8):
        raise ValueError(
            f"not a colour: {text!r}; a hex colour has 3, 4, 6 or 8 digits, not {len(digits)}"
        )
    if len(digits) in (3, 4):
        digits = "".join(c * 2 for c in digits)
    channels = [int(digits[i : i + 2], 16) for i in range(0, len(digits), 2)]
    if len(channels) == 3:
        channels.append(255)
    r, g, b, a = channels
    return (r, g, b, a)


def _function(inside: str, text: str) -> Color:
    parts = inside.replace(",", " ").split()
    if len(parts) not in (3, 4):
        raise ValueError(f"not a colour: {text!r}; rgba() takes 3 or 4 numbers, not {len(parts)}")
    try:
        r, g, b = (int(p) for p in parts[:3])
    except ValueError:
        raise ValueError(
            f"not a colour: {text!r}; red, green and blue are whole numbers 0 to 255"
        ) from None
    try:
        alpha = float(parts[3]) if len(parts) == 4 else 1.0
    except ValueError:
        raise ValueError(f"not a colour: {text!r}; alpha is a number 0.0 to 1.0") from None
    for name, value in (("red", r), ("green", g), ("blue", b)):
        if not 0 <= value <= 255:
            raise ValueError(f"not a colour: {text!r}; {name} is {value}, not 0 to 255")
    if not 0.0 <= alpha <= 1.0:  # also false for nan
        raise ValueError(f"not a colour: {text!r}; alpha is {alpha:g}, not 0.0 to 1.0")
    return (r, g, b, round(alpha * 255))
