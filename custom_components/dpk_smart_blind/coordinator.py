"""DataUpdateCoordinator for eto_irrigation."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    DPKSmartBlindAPI,
    DPKSmartBlindAuthenticationError,
    DPKSmartBlindError,
)
from .const import _LOGGER, DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant

    from .data import DPKSmartBlindConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class DPKTradingDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: DPKSmartBlindConfigEntry

    def __init__(
        self,
        client: DPKSmartBlindAPI,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        self._client = client

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=10),
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self._client.async_get_data()
        except DPKSmartBlindAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except DPKSmartBlindError as exception:
            raise UpdateFailed(exception) from exception

    async def async_check_entity_state_change(
        self, event: Event[EventStateChangedData]
    ) -> None:
        """Fetch and process state change event."""
        _LOGGER.debug("Entity state change: %s", event)
        """self.state_change = True"""

    @property
    def eto_client(self) -> DPKSmartBlindAPI:
        """Getter."""
        return self._client
