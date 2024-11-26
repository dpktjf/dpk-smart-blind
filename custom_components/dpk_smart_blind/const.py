"""Constants for dpk_smart_blind."""

from enum import StrEnum
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)
_LOGGER: Logger = getLogger(__name__)

DOMAIN = "dpk_smart_blind"
DEFAULT_NAME = "DPK Smart Blind"
ATTRIBUTION = "Data provided by the sun"
MANUFACTURER = "DPK"
CONFIG_FLOW_VERSION = 1

DEFAULT_NAME = "DPK Smart Blind"
DEFAULT_RETRY = 60

# entities for data
CONF_AZIMUTH = "set_azimuth"
CONF_DEFAULT_HEIGHT = "default_percentage"
CONF_DELTA_POSITION = "delta_position"
CONF_DELTA_TIME = "delta_time"
CONF_DISTANCE = "distance_shaded_area"
CONF_ENTITY = "cover"
CONF_FOV_LEFT = "fov_left"
CONF_FOV_RIGHT = "fov_right"
CONF_HEIGHT_WIN = "window_height"
CONF_MAX_ELEVATION = "max_elevation"
CONF_MIN_ELEVATION = "min_elevation"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_WEATHER_STATE = "weather_state"


ATTR_AZIMUTH = "azimuth"
ATTR_ELEVATION = "elevation"
ATTR_SHADOW_LENGTH = "calc_shadow_length"
ATTR_COVER_HEIGHT = "calc_cover_height"
ATTR_NOW = "utc_now"
ATTR_COVER_SETTING = "cover_setting"
ATTR_SUN_STATE = "sun_in_window"


class StateOfSunInWindow(StrEnum):
    """Solar location w.r.t. window."""

    EARLY = "early"
    IN_FRONT = "in_front"
    JUST_LEFT = "just_left"
    PASSED = "passed"
