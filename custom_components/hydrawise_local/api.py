"""HTTP client for the Hydrawise controller local API."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import LOCAL_PERIOD_ID

_LOGGER = logging.getLogger(__name__)

SCHEDULE_PATH = "get_sched_json.php"
COMMAND_PATH = "set_manual_data.php"


class HydrawiseLocalError(Exception):
    """Base error for Hydrawise Local API calls."""


class HydrawiseAuthError(HydrawiseLocalError):
    """Authentication failed."""


class HydrawiseCommandError(HydrawiseLocalError):
    """The controller rejected a command."""


class HydrawiseLocalApi:
    """Thin async wrapper around the undocumented local Hydrawise HTTP API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        username: str,
        password: str,
    ) -> None:
        self._session = session
        self._host = host.rstrip("/")
        self._auth = aiohttp.BasicAuth(username, password)

    @property
    def host(self) -> str:
        """Configured controller host."""
        return self._host

    def _url(self, path: str) -> str:
        return f"http://{self._host}/{path}"

    async def async_get_schedule(self) -> dict[str, Any]:
        """Fetch the current schedule and zone status."""
        return await self._async_request("GET", SCHEDULE_PATH)

    async def async_command_zone(
        self,
        action: str,
        relay: int,
        *,
        duration: int | None = None,
    ) -> dict[str, Any]:
        """Send a zone command (run, stop, suspend, ...)."""
        params: dict[str, str | int] = {
            "action": action,
            "relay": relay,
            "period_id": LOCAL_PERIOD_ID,
        }
        if duration is not None:
            params["custom"] = duration
        return await self._async_request("GET", COMMAND_PATH, params=params)

    async def _async_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
    ) -> dict[str, Any]:
        url = self._url(path)
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                auth=self._auth,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status == 401:
                    raise HydrawiseAuthError("Invalid local controller credentials")
                if response.status >= 400:
                    raise HydrawiseLocalError(
                        f"HTTP {response.status} from controller at {self._host}"
                    )
                try:
                    data: dict[str, Any] = await response.json(content_type=None)
                except (aiohttp.ContentTypeError, ValueError) as err:
                    raise HydrawiseLocalError(
                        f"Invalid JSON from controller at {self._host}"
                    ) from err
        except TimeoutError as err:
            raise HydrawiseLocalError(
                f"Timeout talking to controller at {self._host}"
            ) from err
        except aiohttp.ClientError as err:
            raise HydrawiseLocalError(
                f"Connection error for controller at {self._host}: {err}"
            ) from err

        message_type = data.get("message_type") or data.get("messageType")
        if message_type == "error":
            message = data.get("message", "Unknown controller error")
            raise HydrawiseCommandError(message)

        return data
