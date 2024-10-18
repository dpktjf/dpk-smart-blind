"""Constants for dpk_smart_blind."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "dpk_smart_blind"
DEFAULT_NAME = "DPK Smart Blind"
ATTRIBUTION = "Data provided by the sun"
MANUFACTURER = "DPK"
CONFIG_FLOW_VERSION = 1

DEFAULT_NAME = "DPK Smart Blind"
DEFAULT_RETRY = 60

# entities for data
CONF_WINDOW_HEIGHT = "window_height"
CONF_SHADED_AREA = "shaded_area"

ATTR_AZIMUTH = "azimuth"
ATTR_ELEVATION = "elevation"
ATTR_SHADOW_LENGTH = "calc_shadow_length"
ATTR_COVER_HEIGHT = "calc_cover_height"
ATTR_NOW = "utc_now"
ATTR_COVER_SETTING = "cover_setting"
