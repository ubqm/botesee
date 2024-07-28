from typing import Literal

import pytest

from src.image_collectors.compare_imcol import CompareImCol
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
