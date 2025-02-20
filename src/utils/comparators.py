from pydantic import BaseModel, field_validator

from src.utils.enums import ColorTuple


class ComparatorRanges(BaseModel):
    """Storage for comparison values.
    First item of tuple is lower border, second - top border
    """

    green: tuple[float, float]
    white: tuple[float, float]
    orange: tuple[float, float]
    red: tuple[float, float]

    @field_validator("*", mode="after")
    @classmethod
    def validate_borders(cls, ranges: tuple[float, float]) -> tuple[float, float]:
        if ranges[0] > ranges[1]:
            raise ValueError("Lower border should be less or equal than top border")
        return ranges


class Comparator:
    """Class that handles comparison for player values and matches them with colors"""

    def __init__(self, ranges: ComparatorRanges) -> None:
        """Ranges could include intersecting values"""
        self.ranges = ranges

    def get_stat_color(self, player_value: float) -> ColorTuple:
        """Get color for specified stat value.
        If values have intersecting values - best of them will be returned
        """
        match player_value:
            case value if self.ranges.green[0] <= value <= self.ranges.green[1]:
                return ColorTuple.GREEN
            case value if self.ranges.white[0] <= value <= self.ranges.white[1]:
                return ColorTuple.WHITE
            case value if self.ranges.orange[0] <= value <= self.ranges.orange[1]:
                return ColorTuple.ORANGE
            case value if self.ranges.red[0] <= value <= self.ranges.red[1]:
                return ColorTuple.RED
            case _:
                return ColorTuple.WHITE


kd_comparator_values = ComparatorRanges(
    green=(1.3, float("+inf")),
    white=(0.8, 1.3),
    orange=(0.6, 0.8),
    red=(0.0, 0.6),
)
adr_comparator_values = ComparatorRanges(
    green=(90, float("+inf")),
    white=(60, 90),
    orange=(50, 60),
    red=(0, 50),
)
mvp_comparator_values = ComparatorRanges(
    green=(4, float("+inf")),
    white=(1, 4),
    orange=(0, 1),
    red=(float("-inf"), 0),
)

kd_comparator = Comparator(kd_comparator_values)
adr_comparator = Comparator(adr_comparator_values)
mvp_comparator = Comparator(mvp_comparator_values)
