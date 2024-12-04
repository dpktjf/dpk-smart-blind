"""Sample API Client."""

from __future__ import annotations

import logging
from datetime import datetime as dt
from datetime import timedelta as td
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

import astral.sun
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
    ATTR_SUN_STATE,
    CONF_AZIMUTH,
    CONF_DEFAULT_HEIGHT,
    CONF_DELTA_TIME,
    CONF_DISTANCE,
    CONF_FOV_LEFT,
    CONF_FOV_RIGHT,
    CONF_HEIGHT_WIN,
    StateOfSunInWindow,
)

if TYPE_CHECKING:
    import aiohttp
    from homeassistant.core import HomeAssistant, StateMachine

    from .data import DPKSmartBlindConfigEntry

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

    def __init__(
        self,
        config: DPKSmartBlindConfigEntry,
        name: str,
        session: aiohttp.ClientSession,
        states: StateMachine,
        hass: HomeAssistant,
    ) -> None:
        """Sample API Client."""
        location, elevation = get_astral_location(hass)
        self._location = location  # astral.location.Location
        self._elevation = elevation
        self._hass = hass

        self._name = name
        self._config = config
        self._session = session
        self._states = states

        self._last_azimuth = None
        self._now = dt.now(ZoneInfo(self._hass.config.time_zone))

        self._calc_data = {}
        self._calc_data[ATTR_AZIMUTH] = None
        self._calc_data[ATTR_ELEVATION] = None
        self._calc_data[ATTR_SHADOW_LENGTH] = None
        self._calc_data[ATTR_COVER_HEIGHT] = None
        self._calc_data[ATTR_COVER_SETTING] = None
        self._calc_data[ATTR_SUN_STATE] = None

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
            TODO: desk area is different height to cover, so might need
            to play around with that a bit... for now, assume same height
            meaning the blind is actually a little higher than it really is...
            keen to see what happens with that.

            fovleft = self._config.options[CONF_AZIMUTH]-FOV_LEFT
            if attr_azimuth < fovleft:
                early
            elseif attr_azimuth >= fovleft and <= fovright
                in front
            else
                later
                if just moved past fovright
                    set position to default
            azimuth 109.7 / unknown
            110.7 / 110.3
        """

        self._now = dt.now(ZoneInfo(self._hass.config.time_zone))
        self._calc_data[ATTR_NOW] = self._now.isoformat()
        _azimuth = self.azimuth
        _elevation: float = self.elevation
        self._calc_data[ATTR_AZIMUTH] = round(_azimuth, 1)
        self._calc_data[ATTR_ELEVATION] = round(_elevation, 1)
        _LOGGER.debug(
            "Azi window-%s/min-%s/max-%s/current-%s",
            self._config.options[CONF_AZIMUTH],
            self.azi_min_abs,
            self.azi_max_abs,
            round(_azimuth, 1),
        )

        self._calc_data[ATTR_SUN_STATE] = self.sun_in_window_state(
            _azimuth, self.last_azimuth
        )
        self._last_azimuth = _azimuth

        self._calc_data[ATTR_SHADOW_LENGTH] = round(
            self.shadow_length(
                float(self._config.options[CONF_HEIGHT_WIN]), _elevation
            ),
            1,
        )
        """
        TODO: when early, then need some default calcs, such as whatever
        the blind position is should be the cover height and associated
        settings...
        That comes from coordinator.async_check_cover_state_change()
        """
        if self._calc_data[ATTR_SUN_STATE] == StateOfSunInWindow.JUST_LEFT:
            """Need to reset the blind to its default"""
            self._calc_data[ATTR_COVER_HEIGHT] = (
                self._config.options[CONF_DEFAULT_HEIGHT]
                * self._config.options[CONF_HEIGHT_WIN]
                / 100
            )
            self._calc_data[ATTR_COVER_SETTING] = self.cover_setting
        elif self._calc_data[ATTR_SUN_STATE] == StateOfSunInWindow.IN_FRONT:
            """Need to calc these values, but only move if > than last cover
            setting - CONF_DELTA_POSITION"""
            self._calc_data[ATTR_COVER_HEIGHT] = round(
                self._config.options[CONF_DISTANCE] * tan(rad(_elevation)), 1
            )
            self._calc_data[ATTR_COVER_SETTING] = self.cover_setting

    @property
    def azimuth(self) -> float:
        """Compute sun azimuth for current time."""
        return astral.sun.azimuth(self._location.observer, self._now)

    @property
    def elevation(self) -> float:
        """Compute sun elevation for current time."""
        return astral.sun.elevation(self._location.observer, self._now)

    @property
    def azi_min_abs(self) -> int:
        """Calculate min azimuth."""
        return (
            self._config.options[CONF_AZIMUTH]
            - self._config.options[CONF_FOV_LEFT]
            + 360
        ) % 360

    @property
    def azi_max_abs(self) -> int:
        """Calculate max azimuth."""
        return (
            self._config.options[CONF_AZIMUTH]
            + self._config.options[CONF_FOV_RIGHT]
            + 360
        ) % 360

    @property
    def delta_time(self) -> int:
        """Getter for delta time between calculations."""
        return self._config.options[CONF_DELTA_TIME]

    @property
    def last_azimuth(self) -> float:
        """Calculate azimuth from last invocation."""
        if self._last_azimuth is None:
            local_last = dt.now(ZoneInfo(self._hass.config.time_zone))
            local_last -= td(minutes=self.delta_time)
            _LOGGER.debug("local_last=%s", local_last)
            self._last_azimuth = round(
                astral.sun.azimuth(self._location.observer, local_last), 1
            )
        return float(self._last_azimuth)

    @property
    def cover_setting(self) -> float:
        """Calculate cover setting % from window and cover height."""
        return round(
            self._calc_data[ATTR_COVER_HEIGHT]
            / self._config.options[CONF_HEIGHT_WIN]
            * 100,
            0,
        )

    def shadow_length(self, window_height: float, elevation: float) -> float:
        """Calculate shadow length from window height and sun elevation."""
        return window_height / tan(rad(elevation))

    def sun_in_window_state(
        self, azimuth: float, last_azimuth: float
    ) -> StateOfSunInWindow:
        """Calculate where sun is in relation to window field of view."""
        ret: StateOfSunInWindow = StateOfSunInWindow.PASSED
        if azimuth < self.azi_min_abs:
            ret = StateOfSunInWindow.EARLY
        elif azimuth >= self.azi_min_abs and azimuth < self.azi_max_abs:
            ret = StateOfSunInWindow.IN_FRONT
        elif last_azimuth < self.azi_max_abs and azimuth >= self.azi_max_abs:
            ret = StateOfSunInWindow.JUST_LEFT
        return ret
