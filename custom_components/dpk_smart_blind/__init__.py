"""
Custom integration to integrate eto_irrigation with Home Assistant.

For more details about this integration, please refer to
https://github.com/dpktjf/eto-irrigation
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_NAME,
    Platform,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DPKSmartBlindAPI
from .const import (
    CONF_STOP_LOSS,
    CONF_TAKE_PROFIT,
    CONF_TRADE_PRICE,
    CONF_YAHOO_ENTITY_ID,
)
from .coordinator import DPKTradingDataUpdateCoordinator
from .data import DPKTradingData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import DPKTradingConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

# https://homeassistantapi.readthedocs.io/en/latest/api.html

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: DPKTradingConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    _name = entry.data[CONF_NAME]

    eto_api = DPKSmartBlindAPI(
        name=_name,
        yahoo_entity_id=entry.options[CONF_YAHOO_ENTITY_ID],
        trade_price=entry.options[CONF_TRADE_PRICE],
        take_profit=entry.options[CONF_TAKE_PROFIT],
        stop_loss=entry.options[CONF_STOP_LOSS],
        session=async_get_clientsession(hass),
        states=hass.states,
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    coordinator = DPKTradingDataUpdateCoordinator(eto_api, hass)
    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    entry.runtime_data = DPKTradingData(_name, eto_api, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(
    hass: HomeAssistant, entry: DPKTradingConfigEntry
) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DPKTradingConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
