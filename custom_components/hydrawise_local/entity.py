"""Base entity for Hydrawise Local."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import HydrawiseLocalCoordinator
from .data import HydrawiseZoneData


class HydrawiseLocalEntity(CoordinatorEntity[HydrawiseLocalCoordinator]):
    """Common behaviour for Hydrawise Local entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HydrawiseLocalCoordinator,
        zone: HydrawiseZoneData,
        translation_key: str,
    ) -> None:
        super().__init__(coordinator)
        self.zone = zone
        self._attr_translation_key = translation_key
        host = coordinator.api.host
        self._attr_unique_id = f"{host}_{zone.relay_id}_{translation_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{host}_{zone.relay_id}")},
            name=f"{zone.name} (Local)",
            manufacturer=MANUFACTURER,
            model="Hydrawise Zone",
            configuration_url=f"http://{host}/",
        )

    @property
    def zone_data(self) -> HydrawiseZoneData | None:
        """Return the latest data for this zone, if present."""
        if not self.coordinator.data:
            return None
        for zone in self.coordinator.data.zones:
            if zone.relay_id == self.zone.relay_id:
                return zone
        return None
