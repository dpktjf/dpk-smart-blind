"""Sensor platform for dpk_smart_blind."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    _LOGGER,
    ATTR_MANUAL_OVERRIDE,
    ATTR_SUN_IN_WINDOW,
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import DPKTradingDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import DPKSmartBlindConfigEntry

SENSOR_TYPES: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key=ATTR_SUN_IN_WINDOW,
        name="Smart Blind Sun In Window",
        icon="mdi:sun-angle",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    BinarySensorEntityDescription(
        key=ATTR_MANUAL_OVERRIDE,
        name="Smart Blind Manual Override",
        icon="mdi:blinds",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    config_entry: DPKSmartBlindConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    domain_data = config_entry.runtime_data
    name = domain_data.name
    coordinator = domain_data.coordinator

    entities: list[DPKSmartBlindBinarySensor] = [
        DPKSmartBlindBinarySensor(
            name,
            config_entry.entry_id,
            False,
            binary_sensor,
            coordinator,
        )
        for binary_sensor in SENSOR_TYPES
    ]
    async_add_entities(entities)


class DPKSmartBlindBinarySensor(
    CoordinatorEntity[DPKTradingDataUpdateCoordinator], BinarySensorEntity
):
    """Smart Blind Binary Sensor class."""

    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        name: str,
        unique_id: str,
        state: bool,  # noqa: FBT001
        binary_sensor: BinarySensorEntityDescription,
        coordinator: DPKTradingDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator=coordinator)

        self.entity_description = binary_sensor
        self._key = binary_sensor.key
        self._attr_translation_key = binary_sensor.key
        self._name = f"{name} {binary_sensor.name}"
        self._attr_unique_id = f"{unique_id}-{name}-{binary_sensor.name}"
        self._state = state
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DEFAULT_NAME)},
            manufacturer=MANUFACTURER,
        )

    @property
    def name(self) -> str:
        """Name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def is_on(self) -> bool | None:
        """Return the native value of the sensor."""
        return (
            False
            if self.coordinator.data.get(self._key) is None
            else self.coordinator.data.get(self._key)
        )
