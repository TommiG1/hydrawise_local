"""Offline tests for Hydrawise Local."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "hydrawise_local"
_SPEC = importlib.util.spec_from_file_location("hydrawise_local_data", _ROOT / "data.py")
assert _SPEC and _SPEC.loader and _SPEC.name
_DATA = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _DATA
_SPEC.loader.exec_module(_DATA)
parse_schedule = _DATA.parse_schedule
format_duration_de = _DATA.format_duration_de

FIXTURE = {
    "name": "Test Controller",
    "time": 1_700_000_000,
    "running": [
        {
            "relay_id": 10,
            "relay": 2,
            "time_left": 120,
            "current": 3,
            "water": "12 litres",
            "water_int": 12.0,
        }
    ],
    "relays": [
        {
            "relay_id": 10,
            "relay": 2,
            "name": "Zone 2",
            "timestr": "Sat",
            "normalRuntime": 25,
            "run_seconds": 1500,
            "time": 3600,
            "frequency": 259200,
            "lastwaterepoch": 1_699_900_000,
            "suspended": 1,
            "sensor": 0,
            "type": 1,
        }
    ],
}


def test_format_duration_de() -> None:
    assert format_duration_de(0) == "0 Sek"
    assert format_duration_de(52) == "52 Sek"
    assert format_duration_de(125) == "2 Min 5 Sek"
    assert format_duration_de(1500) == "25 Min 0 Sek"
    assert format_duration_de(3720) == "1 Std 2 Min 0 Sek"
    assert format_duration_de(247940) == "2 T 20 Std 52 Min 20 Sek"
    assert format_duration_de(259200) == "3 T 0 Std 0 Min 0 Sek"


def test_parse_schedule_lastwaterepoch_zero_is_none() -> None:
    payload = {
        "name": "Test",
        "time": 1_700_000_000,
        "running": [],
        "relays": [
            {
                "relay_id": 1,
                "relay": 1,
                "name": "Zone 1",
                "lastwaterepoch": 0,
                "time": 0,
            }
        ],
    }
    schedule = parse_schedule(payload)
    assert schedule.zones[0].last_watered_at is None


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
    assert zone.frequency_seconds == 259200
    assert zone.timestr == "Sat"
    assert zone.running_current == 3
    assert zone.running_water == "12 litres"
    assert zone.running_water_int == 12.0
    assert zone.last_watered_at == datetime.fromtimestamp(
        1_699_900_000, tz=timezone.utc
    )
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
