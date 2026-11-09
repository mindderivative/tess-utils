"""Enum words: TDL's upper case to tre's lower case."""

from __future__ import annotations

import re

_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*(_[A-Za-z0-9]+)*")


def to_tre_word(name: object) -> str:
    """``SPACE_BETWEEN`` to ``space_between``, ``HORIZONTAL`` to ``horizontal``. A name is letters,
    digits and single underscores, starting with a letter; anything else is an error."""
    if not isinstance(name, str) or _WORD.fullmatch(name) is None:
        raise ValueError(
            f"not an enum word: {name!r}; write letters, digits and _, like SPACE_BETWEEN"
        )
    return name.lower()
