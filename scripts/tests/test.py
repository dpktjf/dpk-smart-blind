from enum import StrEnum
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)
_LOGGER: Logger = getLogger(__name__)


class StateOfSunInWindow(StrEnum):
    """Solar location w.r.t. window."""

    EARLY = "early"
    IN_FRONT = "in_front"
    JUST_LEFT = "just_left"
    PASSED = "passed"


azi_min_abs = 170
azi_max_abs = 190


def sun_in_window_state(azimuth, last_azimuth) -> StateOfSunInWindow:
    ret: StateOfSunInWindow = StateOfSunInWindow.PASSED
    if azimuth < azi_min_abs:
        ret = StateOfSunInWindow.EARLY
    elif azimuth >= azi_min_abs and azimuth < azi_max_abs:
        ret = StateOfSunInWindow.IN_FRONT
    elif last_azimuth < azi_max_abs and azimuth >= azi_max_abs:
        ret = StateOfSunInWindow.JUST_LEFT
    return ret


print(sun_in_window_state(80, 78))
print(sun_in_window_state(170, 160))
print(sun_in_window_state(180, 170))
print(sun_in_window_state(190, 180))
print(sun_in_window_state(200, 190))
print(sun_in_window_state(210, 200))
