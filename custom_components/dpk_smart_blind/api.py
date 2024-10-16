"""Sample API Client."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import STATE_UNKNOWN

from custom_components.dpk_smart_blind.const import (
    ATTR_ACTION,
    ATTR_ACTION_SIT,
    ATTR_ACTION_STOP,
    ATTR_ACTION_TAKE,
    ATTR_CURRENT_PRICE,
    ATTR_RETURN,
    CONF_STOP_LOSS,
    CONF_TAKE_PROFIT,
    CONF_TRADE_PRICE,
)

if TYPE_CHECKING:
    import aiohttp
    from homeassistant.core import StateMachine

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
        yahoo_entity_id: str,
        trade_price: float,
        take_profit: int,
        stop_loss: int,
        session: aiohttp.ClientSession,
        states: StateMachine,
    ) -> None:
        """Sample API Client."""
        self._name = name
        self._yahoo_entity_id = yahoo_entity_id
        self._trade_price = trade_price
        self._take_profit = take_profit
        self._stop_loss = stop_loss
        self._session = session
        self._states = states
        self._return: float | str = STATE_UNKNOWN

        self._calc_data = {}
        self._calc_data[ATTR_RETURN] = STATE_UNKNOWN
        self._calc_data[ATTR_CURRENT_PRICE] = STATE_UNKNOWN
        self._calc_data[CONF_TRADE_PRICE] = self._trade_price
        self._calc_data[CONF_TAKE_PROFIT] = self._take_profit
        self._calc_data[CONF_STOP_LOSS] = self._stop_loss
        self._calc_data[ATTR_ACTION] = ATTR_ACTION_SIT

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
            self._calc_data[ATTR_CURRENT_PRICE] = await self._get(self._yahoo_entity_id)

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
            return = (current-trade)/trade
        """

        if self._calc_data[ATTR_CURRENT_PRICE] is not STATE_UNKNOWN:
            self._calc_data[ATTR_RETURN] = round(
                (self._calc_data[ATTR_CURRENT_PRICE] - self._trade_price)
                / self._trade_price
                * 100,
                2,
            )
            if self._calc_data[ATTR_RETURN] > self._take_profit:
                self._calc_data[ATTR_ACTION] = ATTR_ACTION_TAKE
            if self._calc_data[ATTR_RETURN] < -self._stop_loss:
                self._calc_data[ATTR_ACTION] = ATTR_ACTION_STOP
