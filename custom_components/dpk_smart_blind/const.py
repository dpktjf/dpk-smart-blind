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
CONF_YAHOO_ENTITY_ID = "yahoo_entity_id"
CONF_TRADE_DATE = "trade_date"
CONF_TRADE_PRICE = "trade_price"
CONF_TRADE_QUANTITY = "trade_quantity"
CONF_STOP_LOSS = "stop_loss"
CONF_TAKE_PROFIT = "take_profit"
CONF_HORIZON = "horizon"

ATTR_RETURN = "return"
ATTR_ASOF = "as_of"
ATTR_CURRENT_PRICE = "current_price"
ATTR_ACTION = "action"

ATTR_ACTION_SIT = "sit"
ATTR_ACTION_STOP = "stop"
ATTR_ACTION_TAKE = "take"
