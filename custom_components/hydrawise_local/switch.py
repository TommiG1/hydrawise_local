"""Switch platform for Hydrawise Local."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import HydrawiseLocalConfigEntry
from .api import HydrawiseCommandError, HydrawiseLocalError
from .entity import HydrawiseLocalEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HydrawiseLocalConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hydrawise Local switches."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        HydrawiseLocalZoneSwitch(coordinator, zone)
        for zone in coordinator.data.zones
    )


class HydrawiseLocalZoneSwitch(HydrawiseLocalEntity, SwitchEntity):
    """Start or stop a zone via the local API."""

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone, "zone_run")

    @property
    def is_on(self) -> bool | None:
        zone = self.zone_data
        if zone is None:
            return None
        return zone.is_running

    async def async_turn_on(self, **kwargs: Any) -> None:
        zone = self.zone_data or self.zone
        duration = zone.default_run_seconds
        try:
            await self.coordinator.api.async_command_zone(
                "run",
                zone.relay,
                duration=duration,
            )
        except (HydrawiseCommandError, HydrawiseLocalError) as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        zone = self.zone_data or self.zone
        try:
            await self.coordinator.api.async_command_zone("stop", zone.relay)
        except (HydrawiseCommandError, HydrawiseLocalError) as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
