# Hydrawise Local

Home Assistant custom integration for Hunter Hydrawise controllers via the **local HTTP API** (firmware &lt; 3.0). Runs **in parallel** to the official cloud integration (`hydrawise`).

## Installation

1. Copy `custom_components/hydrawise_local/` to `/config/custom_components/hydrawise_local/`
2. Restart Home Assistant
3. **Settings → Devices & services → Add integration → Hydrawise Local**
4. Enter controller IP, username (`admin`), and the **local password** from the controller (Settings → Config → Local Password — not your Hydrawise cloud password)

### HACS (custom repository)

Add `https://github.com/TommiG1/hydrawise_local` as a custom integration repository, then install **Hydrawise Local**.

## Entities per zone

| Platform | Name | Purpose |
|----------|------|---------|
| `switch` | Run | Start/stop zone locally (no cloud latency) |
| `binary_sensor` | Watering | Zone is currently running |
| `binary_sensor` | Suspended | Automatic schedule paused |
| `sensor` | Next run | Timestamp |
| `sensor` | Time until next run | Duration |
| `sensor` | Last watered | Timestamp |
| `sensor` | Remaining run time | Duration (while running) |

Device names end with **`(Local)`** so they are easy to tell apart from cloud entities.

## Notes

- Local commands are **not** reflected in the Hydrawise mobile/web app.
- Cloud (`hydrawise`) and local (`hydrawise_local`) entities can coexist — pick one source per automation.
- Control uses `set_manual_data.php` with `period_id=998` and local zone number `relay`.

## Tests

```bash
PYTHONPATH=custom_components pytest tests/ -v
```

## License

Apache-2.0 — see [LICENSE](LICENSE).
