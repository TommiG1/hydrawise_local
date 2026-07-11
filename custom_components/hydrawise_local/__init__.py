"""The Hydrawise Local integration."""

from __future__ import annotations

from dataclasses import dataclass

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HydrawiseLocalApi
from .const import DOMAIN
from .coordinator import HydrawiseLocalCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]


@dataclass
class HydrawiseLocalRuntimeData:
    """Runtime data stored on the config entry."""

    coordinator: HydrawiseLocalCoordinator
    session: aiohttp.ClientSession


type HydrawiseLocalConfigEntry = ConfigEntry[HydrawiseLocalRuntimeData]


async def async_setup_entry(
    hass: HomeAssistant, entry: HydrawiseLocalConfigEntry
) -> bool:
    """Set up Hydrawise Local from a config entry."""
    session = aiohttp.ClientSession(
        connector=async_get_clientsession(hass).connector,
        connector_owner=False,
    )
    try:
        api = HydrawiseLocalApi(
            session,
            entry.data[CONF_HOST],
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
        )
        coordinator = HydrawiseLocalCoordinator(hass, entry, api)
        await coordinator.async_config_entry_first_refresh()

        entry.runtime_data = HydrawiseLocalRuntimeData(
            coordinator=coordinator,
            session=session,
        )
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await session.close()
        raise

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: HydrawiseLocalConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and entry.runtime_data:
        await entry.runtime_data.session.close()
    return unload_ok
