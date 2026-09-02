"""Sensor platform for Hydrawise Local."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import HydrawiseLocalConfigEntry
from .data import format_duration_de
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
    ),
    SensorEntityDescription(
        key="remaining_run_time",
        translation_key="remaining_run_time",
    ),
    SensorEntityDescription(
        key="last_watered",
        translation_key="last_watered",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="default_runtime",
        translation_key="default_runtime",
    ),
    SensorEntityDescription(
        key="run_duration",
        translation_key="run_duration",
    ),
    SensorEntityDescription(
        key="watering_interval",
        translation_key="watering_interval",
    ),
    SensorEntityDescription(
        key="next_run_day",
        translation_key="next_run_day",
    ),
    SensorEntityDescription(
        key="relay_number",
        translation_key="relay_number",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="zone_type",
        translation_key="zone_type",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="sensor_port",
        translation_key="sensor_port",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="running_current",
        translation_key="running_current",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="running_water",
        translation_key="running_water",
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
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
        self._attr_device_class = description.device_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_entity_category = description.entity_category
        self._attr_suggested_display_precision = description.suggested_display_precision

    @property
    def available(self) -> bool:
        """Mark sensors unavailable when the local API omits data."""
        if not super().available:
            return False
        zone = self.zone_data
        if zone is None:
            return False

        key = self.entity_description.key
        if key == "last_watered":
            return zone.last_watered_at is not None
        if key == "next_run_day":
            return bool(zone.timestr)
        if key == "watering_interval":
            return zone.frequency_seconds > 0
        if key == "running_current":
            return zone.is_running and zone.running_current is not None
        if key == "running_water":
            return zone.is_running and zone.running_water_int is not None
        return True

    @property
    def extra_state_attributes(self) -> dict[str, int | bool | str | float] | None:
        """Expose raw values for automations."""
        zone = self.zone_data
        if zone is None:
            return None

        key = self.entity_description.key
        if key == "time_until_next_run":
            return {"seconds": zone.next_run_in_seconds}
        if key == "remaining_run_time":
            return {
                "seconds": zone.remaining_run_seconds,
                "active": zone.is_running,
            }
        if key == "watering_interval":
            return {"seconds": zone.frequency_seconds}
        if key == "default_runtime":
            return {"seconds": zone.default_run_seconds}
        if key == "run_duration":
            return {"seconds": zone.run_seconds}
        if key == "running_water" and zone.running_water:
            return {"raw": zone.running_water}
        return None

    @property
    def native_value(self):
        zone = self.zone_data
        if zone is None:
            return None

        key = self.entity_description.key
        if key == "next_run":
            return zone.next_run_at
        if key == "time_until_next_run":
            return format_duration_de(zone.next_run_in_seconds)
        if key == "remaining_run_time":
            return format_duration_de(zone.remaining_run_seconds)
        if key == "last_watered":
            return zone.last_watered_at
        if key == "default_runtime":
            return format_duration_de(zone.default_run_seconds)
        if key == "run_duration":
            return format_duration_de(zone.run_seconds)
        if key == "watering_interval":
            return format_duration_de(zone.frequency_seconds)
        if key == "next_run_day":
            return zone.timestr or None
        if key == "relay_number":
            return zone.relay
        if key == "zone_type":
            return zone.zone_type
        if key == "sensor_port":
            return zone.sensor
        if key == "running_current":
            return zone.running_current
        if key == "running_water":
            return zone.running_water_int
        return None
