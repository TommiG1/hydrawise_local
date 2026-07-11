"""Parsed Hydrawise local schedule data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class HydrawiseZoneData:
    """Normalized zone state from get_sched_json.php."""

    relay: int
    relay_id: int
    name: str
    normal_runtime_minutes: int
    run_seconds: int
    next_run_in_seconds: int
    next_run_at: datetime
    last_watered_at: datetime | None
    suspended: bool
    is_running: bool
    remaining_run_seconds: int
    zone_type: int
    sensor: int

    @property
    def default_run_seconds(self) -> int:
        """Configured default run duration in seconds."""
        if self.normal_runtime_minutes > 0:
            return self.normal_runtime_minutes * 60
        if self.run_seconds > 0:
            return self.run_seconds
        return 15 * 60


@dataclass(frozen=True, slots=True)
class HydrawiseScheduleData:
    """Controller schedule snapshot."""

    controller_name: str
    controller_time: datetime
    zones: tuple[HydrawiseZoneData, ...]


def parse_schedule(payload: dict[str, Any]) -> HydrawiseScheduleData:
    """Parse the raw local API response into stable zone objects."""
    controller_epoch = int(payload.get("time", 0))
    controller_time = datetime.fromtimestamp(controller_epoch, tz=timezone.utc)
    running_rows = payload.get("running") or []
    running_by_relay_id = {int(row["relay_id"]): row for row in running_rows}

    zones: list[HydrawiseZoneData] = []
    for row in payload.get("relays") or []:
        relay_id = int(row["relay_id"])
        running = running_by_relay_id.get(relay_id)
        next_run_in_seconds = int(row.get("time", 0))
        last_water_epoch = row.get("lastwaterepoch")
        zones.append(
            HydrawiseZoneData(
                relay=int(row["relay"]),
                relay_id=relay_id,
                name=str(row.get("name") or f"Zone {row['relay']}"),
                normal_runtime_minutes=int(row.get("normalRuntime") or 0),
                run_seconds=int(row.get("run_seconds") or row.get("run") or 0),
                next_run_in_seconds=next_run_in_seconds,
                next_run_at=datetime.fromtimestamp(
                    controller_epoch + next_run_in_seconds, tz=timezone.utc
                ),
                last_watered_at=(
                    datetime.fromtimestamp(int(last_water_epoch), tz=timezone.utc)
                    if last_water_epoch
                    else None
                ),
                suspended=bool(int(row.get("suspended") or 0)),
                is_running=running is not None,
                remaining_run_seconds=int((running or {}).get("time_left") or 0),
                zone_type=int(row.get("type") or 0),
                sensor=int(row.get("sensor") or 0),
            )
        )

    return HydrawiseScheduleData(
        controller_name=str(payload.get("name") or "").strip(),
        controller_time=controller_time,
        zones=tuple(zones),
    )
