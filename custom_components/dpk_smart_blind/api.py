"""Sample API Client."""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any

import astral.sun
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.sun import get_astral_location
from numpy import radians as rad
from numpy import tan

from custom_components.dpk_smart_blind.const import (
    ATTR_AZIMUTH,
    ATTR_COVER_HEIGHT,
    ATTR_COVER_SETTING,
    ATTR_ELEVATION,
    ATTR_NOW,
    ATTR_SHADOW_LENGTH,
    CONF_SHADED_AREA,
    CONF_WINDOW_HEIGHT,
)

if TYPE_CHECKING:
    import aiohttp
    from homeassistant.core import HomeAssistant, StateMachine

_LOGGER = logging.getLogger(__name__)


class DPKSmartBlindError(Exception):
    """Exception to indicate a general API error."""


class DPKSmartBlindCommunicationError(
    DPKSmartBlindError,
):
    """Exception to indicate a communication error."""


class DPKSmartBlindAuthenticationError(
    DPKSmartBlindError,
):
    """Exception to indicate an authentication error."""


class DPKSmartBlindCalculationError(
    DPKSmartBlindError,
):
    """Exception to indicate a calculation error."""


class DPKSmartBlindStartupError(
    DPKSmartBlindError,
):
    """Exception to indicate a calculation error - probably due to start-up ."""


class DPKSmartBlindAPI:
    """API Client."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        window_height: float,
        shaded_area: float,
        session: aiohttp.ClientSession,
        states: StateMachine,
        hass: HomeAssistant,
    ) -> None:
        """Sample API Client."""
        location, elevation = get_astral_location(hass)
        self._location = location  # astral.location.Location
        self._elevation = elevation

        self._name = name
        self._window_height = window_height
        self._shaded_area = shaded_area
        self._session = session
        self._states = states

        self._calc_data = {}
        self._calc_data[ATTR_AZIMUTH] = STATE_UNKNOWN
        self._calc_data[ATTR_ELEVATION] = STATE_UNKNOWN
        self._calc_data[ATTR_SHADOW_LENGTH] = STATE_UNKNOWN
        self._calc_data[ATTR_COVER_HEIGHT] = STATE_UNKNOWN
        self._calc_data[ATTR_COVER_SETTING] = STATE_UNKNOWN
        self._calc_data[CONF_WINDOW_HEIGHT] = self._window_height
        self._calc_data[CONF_SHADED_AREA] = self._shaded_area

    async def _get(self, ent: str) -> float:
        st = self._states.get(ent)
        #        if st is not None and isinstance(st.state, float):
        if st is not None:
            if st.state == "unknown":
                msg = "State unknown; probably starting up???"
                raise DPKSmartBlindStartupError(
                    msg,
                )
            return float(st.state)
        msg = "States not yet available; probably starting up???"
        raise DPKSmartBlindCalculationError(
            msg,
        )

    async def collect_calculation_data(self) -> None:
        """Collect all the necessary calculation data."""
        try:
            await self.calc_return()

            _LOGGER.debug("collect_calculation_data: %s", self._calc_data)
        except ValueError as exception:
            msg = f"Value error fetching information - {exception}"
            _LOGGER.exception(msg)
            raise DPKSmartBlindCalculationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            _LOGGER.exception(msg)
            raise DPKSmartBlindError(
                msg,
            ) from exception

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        await self.collect_calculation_data()
        return self._calc_data

    async def calc_return(self) -> None:
        """Perform performance calculation."""
        """
            tan(angleElevation) = windowHeight / shadedArea
        """

        utc_now = datetime.datetime.now(datetime.UTC)
        self._calc_data[ATTR_NOW] = utc_now.isoformat()
        self._calc_data[ATTR_AZIMUTH] = round(
            astral.sun.azimuth(self._location.observer, utc_now), 1
        )
        elevation = astral.sun.elevation(self._location.observer, utc_now)
        self._calc_data[ATTR_ELEVATION] = round(elevation, 1)
        self._calc_data[ATTR_SHADOW_LENGTH] = round(
            self._window_height / tan(rad(elevation)), 1
        )
        self._calc_data[ATTR_COVER_HEIGHT] = round(
            self._shaded_area * tan(rad(elevation)), 1
        )
        self._calc_data[ATTR_COVER_SETTING] = (
            round(self._calc_data[ATTR_COVER_HEIGHT] / self._window_height, 0) * 100
        )
