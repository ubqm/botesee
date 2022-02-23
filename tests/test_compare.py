from ImageCollectors.ImageCollectorCompare import ImageCollectorCompare
import pytest


white = (255, 255, 255, 255)
green = (0, 190, 0, 255)
red = (170, 0, 0, 255)

data_for_compare_stats = [(19.0, 18.0, "1f", [white, white]), (19.0, 12.0, "1f", [green, red]),
                          (19.0, 15.0, "1f", [green, white]), (0, 0, "1f", [white, white]),
                          (0, 184, "1f", [red, green]), (184, 0, "1f", [green, red]),
                          (19.0, 18.0, "2f", [white, white]), (19.0, 12.0, "2f", [green, red]),
                          (19.0, 15.0, "2f", [green, white]), (0, 0, "2f", [white, white]),
                          (0, 184, "2f", [red, green]), (184, 0, "2f", [green, red]),
                          (10, 8, "reverse", [green, white]), (7, 16.0, "reverse", [green, red]),
                          (10, 8, "reverse", [green, white]), (7, 16.0, "reverse", [green, red]),
                          (0, 0, "reverse", [white, white]), (19.0, 12.0, "reverse", [red, green]),
                          (0, 14, "reverse", [green, red]), (18, 0, "reverse", [red, green]),
                          (19.0, 18.0, "total", [white, white]), (19.0, 12.0, "total", [white, white]),
                          (19.0, 15.0, "total", [white, white]), (0, 0, "total", [white, white]),
                          (0, 14, "total", [white, white]), (14, 0, "total", [white, white]),]


@pytest.mark.parametrize("stat1, stat2, category, expected_value", data_for_compare_stats)
def test_compare_stats(stat1, stat2, category, expected_value):
    imgcmpr = ImageCollectorCompare("Ayudesee", "-NAPAD", "100", "games")
    assert imgcmpr.compare_stats((stat1, stat2), category) == expected_value
