import math

import pytest

from tess_utils import expand_radius


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, (0.0, 0.0, 0.0, 0.0)),
        (6, (6.0, 6.0, 6.0, 6.0)),
        (3.5, (3.5, 3.5, 3.5, 3.5)),
        ([1, 2, 3, 4], (1.0, 2.0, 3.0, 4.0)),  # top-left, top-right, bottom-right, bottom-left
        ((0, 0, 8, 8), (0.0, 0.0, 8.0, 8.0)),
    ],
)
def test_one_number_or_four_from_the_top_left_clockwise(
    value: object, expected: tuple[float, ...]
) -> None:
    assert expand_radius(value) == expected


@pytest.mark.parametrize("count", [0, 1, 2, 3, 5])
def test_a_list_of_the_wrong_length_is_an_error(count: int) -> None:
    with pytest.raises(ValueError, match=f"four numbers.*not {count}"):
        expand_radius([1] * count)


@pytest.mark.parametrize(
    ("value", "match"),
    [
        (-1, "cannot be negative"),
        ([1, 2, 3, -4], "cannot be negative"),
        ("6", "not text"),
        (True, "a radius is a number"),
        ([1, 2, 3, "4"], "a radius is a number"),
        (None, "a radius is a number"),
        (math.nan, "not finite"),
        (math.inf, "not finite"),
    ],
)
def test_a_bad_radius_is_an_error(value: object, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        expand_radius(value)
