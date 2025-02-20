from contextlib import nullcontext as does_not_raise
from typing import ContextManager, Literal

import pytest

from src.image_collectors.compare_imcol import CompareImCol
from src.utils.comparators import Comparator, ComparatorRanges
from src.utils.enums import ColorTuple


@pytest.mark.parametrize(
    "values, category, expected",
    [
        ((100, 100), "%", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((33, 33), "%", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((0, 0), "%", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((100, 100), "1f", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((33, 33), "1f", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((0, 0), "1f", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((100, 100), "reverse", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((33, 33), "reverse", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((0, 0), "reverse", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((14, 10), "%", (ColorTuple.GREEN, ColorTuple.RED)),
        ((12, 10), "%", (ColorTuple.GREEN, ColorTuple.WHITE)),
        ((14, 10), "1f", (ColorTuple.GREEN, ColorTuple.RED)),
        ((12, 10), "1f", (ColorTuple.GREEN, ColorTuple.WHITE)),
        ((14, 10), "reverse", (ColorTuple.RED, ColorTuple.GREEN)),
        ((12, 10), "reverse", (ColorTuple.WHITE, ColorTuple.GREEN)),
        ((50, 0), "%", (ColorTuple.GREEN, ColorTuple.RED)),
        ((0, 50), "%", (ColorTuple.RED, ColorTuple.GREEN)),
        ((50, 0), "1f", (ColorTuple.GREEN, ColorTuple.RED)),
        ((0, 50), "1f", (ColorTuple.RED, ColorTuple.GREEN)),
        ((50, 0), "reverse", (ColorTuple.RED, ColorTuple.GREEN)),
        ((0, 50), "reverse", (ColorTuple.GREEN, ColorTuple.RED)),
        ((33, 33), "total", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((0, 50), "total", (ColorTuple.WHITE, ColorTuple.WHITE)),
        ((50, 0), "total", (ColorTuple.WHITE, ColorTuple.WHITE)),
    ],
)
def test_compare_stats(
    values: tuple[float, float],
    category: Literal["1f", "2f", "%", "reverse", "total"],
    expected: tuple[ColorTuple, ColorTuple],
):
    assert expected == CompareImCol.compare_stats(values, category)


@pytest.mark.parametrize(
    ("green", "white", "orange", "red", "expectation"),
    (
        ((100, float("+inf")), (60, 100), (50, 60), (0, 60), does_not_raise()),
        ((100, 90), (90, 100), (50, 60), (0, 60), pytest.raises(ValueError)),
        (
            (100, float("+inf")),
            (101, 100),
            (50, 60),
            (0, 60),
            pytest.raises(ValueError),
        ),
        ((100, float("+inf")), (60, 100), (61, 60), (0, 60), pytest.raises(ValueError)),
        (
            (100, float("+inf")),
            (60, 100),
            (50, 60),
            (61, 60),
            pytest.raises(ValueError),
        ),
    ),
)
def test_comparator_ranges(
    green: tuple[float, float],
    white: tuple[float, float],
    orange: tuple[float, float],
    red: tuple[float, float],
    expectation: ContextManager,
):
    print(type(expectation))
    with expectation:
        comp_range = ComparatorRanges(
            green=green,
            white=white,
            orange=orange,
            red=red,
        )

        assert comp_range.green == green
        assert comp_range.white == white
        assert comp_range.orange == orange
        assert comp_range.red == red


kd_comparator_values = ComparatorRanges(
    green=(1.3, float("+inf")),
    white=(0.8, 1.3),
    orange=(0.6, 0.8),
    red=(0.0, 0.6),
)


@pytest.mark.parametrize(
    ("range_values", "player_value", "expected_color"),
    (
        (kd_comparator_values, 1.5, ColorTuple.GREEN),
        (kd_comparator_values, 1.3, ColorTuple.GREEN),
        (kd_comparator_values, 1.0, ColorTuple.WHITE),
        (kd_comparator_values, 0.8, ColorTuple.WHITE),
        (kd_comparator_values, 0.7, ColorTuple.ORANGE),
        (kd_comparator_values, 0.6, ColorTuple.ORANGE),
        (kd_comparator_values, 0.4, ColorTuple.RED),
        (kd_comparator_values, 0.0, ColorTuple.RED),
        (kd_comparator_values, -0.1, ColorTuple.WHITE),
    ),
)
def test_comparator_colors(
    range_values: ComparatorRanges,
    player_value: float,
    expected_color: ColorTuple,
):
    assert Comparator(range_values).get_stat_color(player_value) == expected_color
