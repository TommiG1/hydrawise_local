"""Binary sensor platform for Hydrawise Local."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import HydrawiseLocalConfigEntry
from .entity import HydrawiseLocalEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HydrawiseLocalConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hydrawise Local binary sensors."""
    coordinator = entry.runtime_data.coordinator
    entities: list[BinarySensorEntity] = []
    for zone in coordinator.data.zones:
        entities.append(HydrawiseLocalWateringBinarySensor(coordinator, zone))
        entities.append(HydrawiseLocalSuspendedBinarySensor(coordinator, zone))
    async_add_entities(entities)


class HydrawiseLocalWateringBinarySensor(HydrawiseLocalEntity, BinarySensorEntity):
    """Whether a zone is currently watering."""

    _attr_device_class = BinarySensorDeviceClass.MOISTURE

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone, "watering")

    @property
    def is_on(self) -> bool | None:
        zone = self.zone_data
        if zone is None:
            return None
        return zone.is_running


class HydrawiseLocalSuspendedBinarySensor(HydrawiseLocalEntity, BinarySensorEntity):
    """Whether automatic watering is suspended for a zone."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone, "suspended")

    @property
    def is_on(self) -> bool | None:
        zone = self.zone_data
        if zone is None:
            return None
        return zone.suspended
