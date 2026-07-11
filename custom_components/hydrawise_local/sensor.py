"""Sensor platform for Hydrawise Local."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import HydrawiseLocalConfigEntry
from .entity import HydrawiseLocalEntity

PARALLEL_UPDATES = 0

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="next_run",
        translation_key="next_run",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="time_until_next_run",
        translation_key="time_until_next_run",
        device_class=SensorDeviceClass.DURATION,
    ),
    SensorEntityDescription(
        key="last_watered",
        translation_key="last_watered",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="remaining_run_time",
        translation_key="remaining_run_time",
        device_class=SensorDeviceClass.DURATION,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HydrawiseLocalConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hydrawise Local sensors."""
    coordinator = entry.runtime_data.coordinator
    entities: list[SensorEntity] = []
    for zone in coordinator.data.zones:
        for description in SENSOR_TYPES:
            entities.append(
                HydrawiseLocalZoneSensor(coordinator, zone, description)
            )
    async_add_entities(entities)


class HydrawiseLocalZoneSensor(HydrawiseLocalEntity, SensorEntity):
    """Expose schedule details for a zone."""

    entity_description: SensorEntityDescription

    def __init__(self, coordinator, zone, description: SensorEntityDescription) -> None:
        super().__init__(coordinator, zone, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        zone = self.zone_data
        if zone is None:
            return None

        key = self.entity_description.key
        if key == "next_run":
            return zone.next_run_at
        if key == "time_until_next_run":
            return timedelta(seconds=zone.next_run_in_seconds)
        if key == "last_watered":
            return zone.last_watered_at
        if key == "remaining_run_time":
            if not zone.is_running:
                return None
            return timedelta(seconds=zone.remaining_run_seconds)
        return None
