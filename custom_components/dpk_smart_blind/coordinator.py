"""DataUpdateCoordinator for eto_irrigation."""

from __future__ import annotations

from datetime import datetime as dt
from datetime import timedelta as td
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    DPKSmartBlindAPI,
    DPKSmartBlindAuthenticationError,
    DPKSmartBlindError,
)
from .const import _LOGGER, DOMAIN, LOGGER
from .data import StateChangedData

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
        self._update_listener: CALLBACK_TYPE | None = None
        self._cover_change_data: StateChangedData | None = None
        self._end_time = None

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=td(minutes=5),
        )
        """update_interval=timedelta(minutes=client.delta_time),"""

        _end = dt.now(ZoneInfo(self.hass.config.time_zone))
        _end += td(minutes=client.delta_time)
        _LOGGER.debug("%s: async_timed_refresh set for %s", client.name, _end)
        self._update_listener = async_track_point_in_time(
            self.hass, self.async_timed_refresh, _end
        )

    async def async_timed_refresh(self, event) -> None:
        """Update from hass controller as a timed event."""
        _LOGGER.debug("%s: async_timed_refresh tripped", self._client.name)

    @callback
    def async_cancel_update_listener(self) -> None:
        """Cancel the scheduled update."""
        _LOGGER.debug("%s: async_cancel_update_listener", self._client.name)
        if self._update_listener:
            _LOGGER.debug("%s: calling _update_listener()", self._client.name)
            """
            Calling the return of async_track_point_in_time() does not invoke
            the callback, but rather cancels the point in time. Should call this
            when the entity is deleted/reloaded or otherwise reset
            """
            self._update_listener()
            self._update_listener = None

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
        _LOGGER.debug("%s: Entity state change: %s", self._client.name, event)
        """self.state_change = True"""

    async def async_check_cover_state_change(
        self, event: Event[EventStateChangedData]
    ) -> None:
        """Fetch and process state change event for cover entities."""
        data = StateChangedData(
            event.data["entity_id"], event.data["old_state"], event.data["new_state"]
        )
        """if data.old_state is None:
            _LOGGER.debug("Old state is None")
            return"""
        if data.new_state.state in ["opening", "closing"]:  # type: ignore[attr-defined]
            _LOGGER.debug("Ignoring intermediate state change for %s", data.entity_id)
            return
        self._cover_change_data = data
        _LOGGER.debug(
            "%s: Cover Entity state change: %s",
            self._client.name,
            self._cover_change_data,
        )
        """self.state_change = True"""
        """
        Need to check new state== open or closed; will be opening or closing
        whilst the cover does its thing, but only interested when it gets set to
        open or closed. When that happens, means either blind has changed by
        this prcess, else manually. If manually, then want to set a
        parameterized timeout and not make any further changes until that
        timeout timesout.
        TODO: how to differentiate between this component requesting a blind
        change, and someone doing it manually?
        """

    @property
    def eto_client(self) -> DPKSmartBlindAPI:
        """Getter."""
        return self._client
