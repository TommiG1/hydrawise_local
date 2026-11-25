"""Offline tests for the sensor platform (Home Assistant is stubbed)."""

from __future__ import annotations

import importlib.util
import sys
import types
from dataclasses import dataclass
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "hydrawise_local"
_PKG = "hydrawise_local_sensor_pkg"


def _stub_module(name: str, **attrs) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__dict__.update(attrs)
    sys.modules[name] = module
    return module


@dataclass(frozen=True)
class _EntityDescription:
    key: str
    translation_key: str | None = None
    device_class: str | None = None
    native_unit_of_measurement: str | None = None
    suggested_display_precision: int | None = None
    entity_category: str | None = None


class _BaseEntity:
    """Stand-in for HydrawiseLocalEntity / CoordinatorEntity."""

    def __init__(self, coordinator, zone, translation_key) -> None:
        self.coordinator = coordinator
        self.zone = zone

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def zone_data(self):
        if not self.coordinator.data:
            return None
        for zone in self.coordinator.data.zones:
            if zone.relay_id == self.zone.relay_id:
                return zone
        return None


def _load_modules():
    _stub_module("homeassistant")
    _stub_module("homeassistant.components")
    _stub_module(
        "homeassistant.components.sensor",
        SensorDeviceClass=types.SimpleNamespace(TIMESTAMP="timestamp", WATER="water"),
        SensorEntity=object,
        SensorEntityDescription=_EntityDescription,
    )
    _stub_module(
        "homeassistant.const",
        EntityCategory=types.SimpleNamespace(DIAGNOSTIC="diagnostic"),
        UnitOfVolume=types.SimpleNamespace(LITERS="L"),
    )
    _stub_module("homeassistant.core", HomeAssistant=object)
    _stub_module("homeassistant.helpers")
    _stub_module(
        "homeassistant.helpers.entity_platform", AddConfigEntryEntitiesCallback=object
    )

    package = _stub_module(_PKG, HydrawiseLocalConfigEntry=object)
    package.__path__ = [str(_ROOT)]
    _stub_module(f"{_PKG}.entity", HydrawiseLocalEntity=_BaseEntity)

    modules = {}
    for name in ("data", "sensor"):
        spec = importlib.util.spec_from_file_location(
            f"{_PKG}.{name}", _ROOT / f"{name}.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        modules[name] = module
    return modules["data"], modules["sensor"]


_DATA, _SENSOR = _load_modules()
_DESCRIPTIONS = {d.key: d for d in _SENSOR.SENSOR_TYPES}


def _make_sensor(key: str, relay: dict, last_update_success: bool = True):
    schedule = _DATA.parse_schedule(
        {"name": "Test", "time": 1_700_000_000, "running": [], "relays": [relay]}
    )
    coordinator = types.SimpleNamespace(
        data=schedule, last_update_success=last_update_success
    )
    return _SENSOR.HydrawiseLocalZoneSensor(
        coordinator, schedule.zones[0], _DESCRIPTIONS[key]
    )


_BASE_RELAY = {"relay_id": 1, "relay": 1, "name": "Zone 1", "time": 3600}


@pytest.mark.parametrize("lastwaterepoch", [0, None, "0"])
def test_last_watered_without_timestamp_is_unknown(lastwaterepoch) -> None:
    sensor = _make_sensor(
        "last_watered", {**_BASE_RELAY, "lastwaterepoch": lastwaterepoch}
    )
    assert sensor.available is True
    assert sensor.native_value is None


def test_last_watered_missing_key_is_unknown() -> None:
    sensor = _make_sensor("last_watered", dict(_BASE_RELAY))
    assert sensor.available is True
    assert sensor.native_value is None


def test_last_watered_with_timestamp() -> None:
    sensor = _make_sensor(
        "last_watered", {**_BASE_RELAY, "lastwaterepoch": 1_699_900_000}
    )
    assert sensor.available is True
    assert sensor.native_value is not None


@pytest.mark.parametrize("timestr", ["", "   ", None])
def test_next_run_day_empty_is_unknown(timestr) -> None:
    sensor = _make_sensor("next_run_day", {**_BASE_RELAY, "timestr": timestr})
    assert sensor.available is True
    assert sensor.native_value is None


def test_next_run_day_with_value() -> None:
    sensor = _make_sensor("next_run_day", {**_BASE_RELAY, "timestr": "Sat"})
    assert sensor.available is True
    assert sensor.native_value == "Sat"


@pytest.mark.parametrize("key", ["last_watered", "next_run_day"])
def test_unavailable_when_coordinator_fails(key) -> None:
    sensor = _make_sensor(key, dict(_BASE_RELAY), last_update_success=False)
    assert sensor.available is False


@pytest.mark.parametrize("key", ["last_watered", "next_run_day"])
def test_unavailable_when_zone_missing(key) -> None:
    sensor = _make_sensor(key, dict(_BASE_RELAY))
    sensor.zone = types.SimpleNamespace(relay_id=999)
    assert sensor.available is False
