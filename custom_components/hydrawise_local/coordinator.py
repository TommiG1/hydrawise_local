"""Data update coordinator for Hydrawise Local."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HydrawiseAuthError, HydrawiseLocalApi, HydrawiseLocalError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN, MIN_SCAN_INTERVAL
from .data import HydrawiseScheduleData, parse_schedule

_LOGGER = logging.getLogger(__name__)


def _scan_interval_seconds(entry: ConfigEntry) -> int:
    interval = int(
        entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
    )
    return max(MIN_SCAN_INTERVAL, interval)


class HydrawiseLocalCoordinator(DataUpdateCoordinator[HydrawiseScheduleData]):
    """Poll the controller for schedule and zone status."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: HydrawiseLocalApi,
    ) -> None:
        self.api = api
        interval = _scan_interval_seconds(entry)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
            config_entry=entry,
        )

    async def _async_update_data(self) -> HydrawiseScheduleData:
        try:
            payload = await self.api.async_get_schedule()
        except HydrawiseAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except HydrawiseLocalError as err:
            raise UpdateFailed(str(err)) from err
        return parse_schedule(payload)
