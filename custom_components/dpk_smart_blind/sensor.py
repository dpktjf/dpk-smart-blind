"""Sensor platform for dpk_smart_blind."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from custom_components.dpk_smart_blind.const import (
    ATTR_ACTION,
    ATTR_CURRENT_PRICE,
    ATTR_RETURN,
    ATTRIBUTION,
    CONF_STOP_LOSS,
    CONF_TAKE_PROFIT,
    CONF_TRADE_PRICE,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DPKTradingDataUpdateCoordinator
    from .data import DPKTradingConfigEntry

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=DOMAIN,
        name="Trading return",
        icon="mdi:currency-usd",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    config_entry: DPKTradingConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    domain_data = config_entry.runtime_data
    name = domain_data.name
    coordinator = domain_data.coordinator

    entities: list[DPKTradingSensor] = [
        DPKTradingSensor(
            name,
            config_entry.entry_id,
            description,
            coordinator,
        )
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class DPKTradingSensor(SensorEntity):
    """ETO Smart Zone Sensor class."""

    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        name: str,
        entry_id: str,
        entity_description: SensorEntityDescription,
        coordinator: DPKTradingDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        self.entity_description = entity_description
        self._coordinator = coordinator
        self.states: dict[str, Any] = {}

        self._attr_name = f"{name} {entity_description.name}"
        self._attr_unique_id = f"{entry_id}-{name}-{entity_description.name}"

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, DEFAULT_NAME)},
            manufacturer=MANUFACTURER,
            name=DEFAULT_NAME,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Get the latest data from OWM and updates the states."""
        await self._coordinator.async_request_refresh()

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self._coordinator.data[ATTR_RETURN]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device specific state attributes."""
        attributes: dict[str, Any] = {}

        attributes[ATTR_ACTION] = self._coordinator.data[ATTR_ACTION]
        attributes[ATTR_CURRENT_PRICE] = self._coordinator.data[ATTR_CURRENT_PRICE]
        attributes[CONF_TRADE_PRICE] = self._coordinator.data[CONF_TRADE_PRICE]
        attributes[CONF_TAKE_PROFIT] = self._coordinator.data[CONF_TAKE_PROFIT]
        attributes[CONF_STOP_LOSS] = self._coordinator.data[CONF_STOP_LOSS]

        return attributes
