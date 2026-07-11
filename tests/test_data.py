"""Offline tests for Hydrawise Local."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "hydrawise_local"
_SPEC = importlib.util.spec_from_file_location("hydrawise_local_data", _ROOT / "data.py")
assert _SPEC and _SPEC.loader
_DATA = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_DATA)
parse_schedule = _DATA.parse_schedule

FIXTURE = {
    "name": "Test Controller",
    "time": 1_700_000_000,
    "running": [{"relay_id": 10, "relay": 2, "time_left": 120, "current": 0}],
    "relays": [
        {
            "relay_id": 10,
            "relay": 2,
            "name": "Zone 2",
            "normalRuntime": 25,
            "run_seconds": 1500,
            "time": 3600,
            "lastwaterepoch": 1_699_900_000,
            "suspended": 1,
            "sensor": 0,
            "type": 1,
        }
    ],
}


def test_parse_schedule_running_and_suspended() -> None:
    schedule = parse_schedule(FIXTURE)
    assert schedule.controller_name == "Test Controller"
    assert len(schedule.zones) == 1
    zone = schedule.zones[0]
    assert zone.name == "Zone 2"
    assert zone.is_running is True
    assert zone.remaining_run_seconds == 120
    assert zone.suspended is True
    assert zone.default_run_seconds == 25 * 60
    assert zone.next_run_at == datetime.fromtimestamp(
        FIXTURE["time"] + 3600, tz=timezone.utc
    )


def test_parse_schedule_fixture_file_if_present() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "schedule.json"
    if not fixture_path.exists():
        return
    payload = json.loads(fixture_path.read_text())
    schedule = parse_schedule(payload)
    assert schedule.zones
