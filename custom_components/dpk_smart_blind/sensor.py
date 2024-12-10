"""Sensor platform for dpk_smart_blind."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    _LOGGER,
    ATTR_AZIMUTH,
    ATTR_COVER_HEIGHT,
    ATTR_COVER_SETTING,
    ATTR_ELEVATION,
    ATTR_NOW,
    ATTR_SHADOW_LENGTH,
    ATTR_SUN_STATE,
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

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_SHADOW_LENGTH,
        name="Smart Blind Shadow Length",
        icon="mdi:sun-angle",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.METERS,
    ),
    SensorEntityDescription(
        key=ATTR_ELEVATION,
        name="Smart Blind Elevation",
        icon="mdi:sun-angle",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_AZIMUTH,
        name="Smart Blind Azimuth",
        icon="mdi:sun-angle",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_COVER_SETTING,
        name="Smart Blind Height",
        icon="mdi:blinds",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
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

    entities: list[DPKSmartBlindSensor] = [
        DPKSmartBlindSensor(
            name,
            config_entry.entry_id,
            sensor,
            coordinator,
        )
        for sensor in SENSOR_TYPES
    ]
    async_add_entities(entities)


class DPKSmartBlindSensor(
    CoordinatorEntity[DPKTradingDataUpdateCoordinator], SensorEntity
):
    """Smart Blind Sensor class."""

    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        name: str,
        entry_id: str,
        sensor: SensorEntityDescription,
        coordinator: DPKTradingDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        self.entity_description = sensor
        self._key = sensor.key
        self._coordinator = coordinator
        self.states: dict[str, Any] = {}

        self._attr_name = f"{name} {sensor.name}"
        self._attr_unique_id = f"{entry_id}-{name}-{sensor.name}"

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
        return self._coordinator.data.get(self._key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device specific state attributes."""
        attributes: dict[str, Any] = {}
        if self._key == ATTR_SHADOW_LENGTH:
            attributes[ATTR_NOW] = self._coordinator.data[ATTR_NOW]
            attributes[ATTR_AZIMUTH] = self._coordinator.data[ATTR_AZIMUTH]
            attributes[ATTR_ELEVATION] = self._coordinator.data[ATTR_ELEVATION]
            attributes[ATTR_COVER_HEIGHT] = self._coordinator.data[ATTR_COVER_HEIGHT]
            attributes[ATTR_COVER_SETTING] = self._coordinator.data[ATTR_COVER_SETTING]
            attributes[ATTR_SUN_STATE] = self._coordinator.data[ATTR_SUN_STATE]

        return attributes
