"""
Custom integration to integrate eto_irrigation with Home Assistant.

For more details about this integration, please refer to
https://github.com/dpktjf/eto-irrigation
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_NAME,
    Platform,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import (
    async_track_state_change_event,
)

from .api import DPKSmartBlindAPI
from .const import _LOGGER
from .coordinator import DPKTradingDataUpdateCoordinator
from .data import DPKSmartBlindData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import DPKSmartBlindConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

# https://homeassistantapi.readthedocs.io/en/latest/api.html


DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: DPKSmartBlindConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    _LOGGER.debug("setting up smart blind %s", entry.data[CONF_NAME])
    api = DPKSmartBlindAPI(
        name=entry.data[CONF_NAME],
        config=entry,
        session=async_get_clientsession(hass),
        states=hass.states,
        hass=hass,
    )

    coordinator = DPKTradingDataUpdateCoordinator(api, hass)
    _entities = ["sun.sun"]
    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            _entities,
            coordinator.async_check_entity_state_change,
        )
    )

    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    entry.runtime_data = DPKSmartBlindData(entry.data[CONF_NAME], api, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(
    hass: HomeAssistant, entry: DPKSmartBlindConfigEntry
) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DPKSmartBlindConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
