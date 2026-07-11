"""Config flow for Hydrawise Local."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HydrawiseAuthError, HydrawiseLocalApi, HydrawiseLocalError
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=300)
        ),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=300)
        ),
    }
)


class HydrawiseLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hydrawise Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            await self.async_set_unique_id(host.lower(), raise_on_progress=False)
            self._abort_if_unique_id_configured()

            title = await self._async_validate_connection(
                host,
                user_input[CONF_USERNAME].strip(),
                user_input[CONF_PASSWORD],
                errors,
            )
            if not errors:
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_HOST: host,
                        CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    async def _async_validate_connection(
        self,
        host: str,
        username: str,
        password: str,
        errors: dict[str, str],
    ) -> str:
        session = async_get_clientsession(self.hass)
        api = HydrawiseLocalApi(session, host, username, password)
        try:
            payload = await api.async_get_schedule()
        except HydrawiseAuthError:
            errors["base"] = "invalid_auth"
        except HydrawiseLocalError:
            errors["base"] = "cannot_connect"
        except aiohttp.ClientError:
            errors["base"] = "cannot_connect"
        else:
            controller_name = str(payload.get("name") or "").strip()
            return controller_name or f"Hydrawise Local ({host})"
        return ""

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> HydrawiseLocalOptionsFlow:
        return HydrawiseLocalOptionsFlow()


class HydrawiseLocalOptionsFlow(OptionsFlow):
    """Handle options for Hydrawise Local."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        interval = int(
            self.config_entry.options.get(
                CONF_SCAN_INTERVAL,
                self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA,
                {CONF_SCAN_INTERVAL: interval},
            ),
        )
