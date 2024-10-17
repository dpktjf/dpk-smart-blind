"""Custom types for eto_irrigation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import DPKSmartBlindAPI
    from .coordinator import DPKTradingDataUpdateCoordinator


type DPKSmartBlindConfigEntry = ConfigEntry[DPKSmartBlindData]


@dataclass
class DPKSmartBlindData:
    """Data for the ETO Smart Zone Calculator."""

    name: str
    client: DPKSmartBlindAPI
    coordinator: DPKTradingDataUpdateCoordinator
