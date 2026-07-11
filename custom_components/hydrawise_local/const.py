"""Constants for the Hydrawise Local integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "hydrawise_local"

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_USERNAME = "admin"
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 15

LOCAL_PERIOD_ID = 998

DEFAULT_RUN_SECONDS = 15 * 60

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

MANUFACTURER = "Hunter"
