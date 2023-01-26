from dataclasses import dataclass
from enum import Enum, EnumMeta


class CustomEnumMeta(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class CustomEnum(Enum, metaclass=CustomEnumMeta):
    """
    Allows to search among Values (not Keys)
    Example: if "de_mirage" in AvailableMaps:
    """
    pass

    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class ColorTuple:
    WHITE = (255, 255, 255, 255)
    GREEN = (0, 190, 0, 255)
    ORANGE = (255, 165, 0, 255)
    RED = (170, 0, 0, 255)


class AvailableMaps(CustomEnum):
    ANCIENT = "de_ancient"
    DUST_2 = "de_dust2"
    INFERNO = "de_inferno"
    MIRAGE = "de_mirage"
    NUKE = "de_nuke"
    OVERPASS = "de_overpass"
    TRAIN = "de_train"
    VERTIGO = "de_vertigo"
    ANUBIS = "de_anubis"


if __name__ == '__main__':
    d1 = {"de_mirage": 2}
