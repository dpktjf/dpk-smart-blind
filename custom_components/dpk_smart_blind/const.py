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
CONF_SHADOW_LENGTH = "shadow_length"

ATTR_AZIMUTH = "azimuth"
ATTR_ELEVATION = "elevation"
ATTR_SHADOW_LENGTH = "calc_shadow_length"
ATTR_WINDOW_HEIGHT = "calc_window_height"
ATTR_NOW = "utc_now"

ATTR_ACTION_SIT = "sit"
ATTR_ACTION_STOP = "stop"
ATTR_ACTION_TAKE = "take"
