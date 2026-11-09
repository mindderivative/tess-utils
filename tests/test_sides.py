import math

import pytest

from tess_utils import expand_sides, to_tre_order


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (8, (8.0, 8.0, 8.0, 8.0)),
        (2.5, (2.5, 2.5, 2.5, 2.5)),
        (0, (0.0, 0.0, 0.0, 0.0)),
        ([1, 2, 3, 4], (1.0, 2.0, 3.0, 4.0)),
        ((1, 2, 3, 4), (1.0, 2.0, 3.0, 4.0)),
        ({"Top": 8, "Left": 24}, (24.0, 8.0, 0.0, 0.0)),  # unnamed sides are 0
        ({"left": 1, "top": 2, "right": 3, "bottom": 4}, (1.0, 2.0, 3.0, 4.0)),
        ({"BOTTOM": 5}, (0.0, 0.0, 0.0, 5.0)),
        ({}, (0.0, 0.0, 0.0, 0.0)),
        (-4, (-4.0, -4.0, -4.0, -4.0)),  # whether a side may be negative is the caller's rule
    ],
)
def test_one_number_four_numbers_or_named_sides_give_left_top_right_bottom(
    value: object, expected: tuple[float, ...]
) -> None:
    assert expand_sides(value) == expected


@pytest.mark.parametrize("count", [0, 1, 2, 3, 5])
def test_a_list_of_the_wrong_length_is_an_error(count: int) -> None:
    with pytest.raises(ValueError, match=f"four numbers.*not {count}"):
        expand_sides([1] * count)


@pytest.mark.parametrize(
    ("value", "match"),
    [
        ({"Middle": 1}, "unknown side 'middle'"),
        ({"Top": "8"}, "side Top is a number"),
        ({"Top": True}, "side Top is a number"),
        ([1, 2, "3", 4], "a side is a number"),
        ([1, 2, 3, None], "a side is a number"),
        ("8", "numbers, not text"),
        (True, "a side is a number"),
        (None, "a side is a number"),
        (math.inf, "not finite"),
        (math.nan, "not finite"),
        ([1, 2, 3, math.nan], "not finite"),
    ],
)
def test_a_bad_side_is_an_error_that_names_it(value: object, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        expand_sides(value)


def test_tres_order_is_top_right_bottom_left() -> None:
    assert to_tre_order((1.0, 2.0, 3.0, 4.0)) == (2.0, 3.0, 4.0, 1.0)
    assert to_tre_order(expand_sides({"Left": 24, "Top": 8})) == (8.0, 0.0, 0.0, 24.0)
    # four applications of the rotation come back to the start only through the inverse: this
    # pins the direction, not a round trip
    assert to_tre_order((10.0, 0.0, 0.0, 0.0)) == (0.0, 0.0, 0.0, 10.0)
