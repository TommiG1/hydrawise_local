# Hydrawise Local

**Sprachen:** [English](README.md) · Deutsch

Home-Assistant-Custom-Integration für Hunter-Hydrawise-Controller über die **lokale HTTP-API** (Firmware unter 3.0). Läuft **parallel** zur offiziellen Cloud-Integration (`hydrawise`).

## Installation

1. `custom_components/hydrawise_local/` nach `/config/custom_components/hydrawise_local/` kopieren
2. Home Assistant neu starten
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen → Hydrawise Local**
4. Controller-IP, Benutzername (`admin`) und das **lokale Passwort** eingeben (am Controller: Settings → Config → Local Password — nicht das Hydrawise-Cloud-Passwort)

### HACS (Custom Repository)

`https://github.com/TommiG1/hydrawise_local` als Custom-Integration-Repository hinzufügen, dann **Hydrawise Local** installieren.

## Entitäten pro Zone

| Plattform | Name | Funktion |
|-----------|------|----------|
| `switch` | Starten | Zone lokal starten/stoppen (ohne Cloud-Latenz) |
| `binary_sensor` | Bewässert | Zone läuft gerade |
| `binary_sensor` | Ausgesetzt | Automatik pausiert |
| `sensor` | Nächster Lauf | Zeitstempel |
| `sensor` | Zeit bis nächster Lauf | Dauer |
| `sensor` | Zuletzt bewässert | Zeitstempel |
| `sensor` | Verbleibende Laufzeit | Dauer (nur wenn aktiv) |

Gerätenamen enden mit **`(Local)`**, damit sie sich von Cloud-Entitäten unterscheiden.

## Hinweise

- Lokale Befehle erscheinen **nicht** in der Hydrawise-App.
- Cloud- (`hydrawise`) und lokale (`hydrawise_local`) Entitäten können parallel existieren — pro Automation eine Quelle wählen.
- Steuerung nutzt `set_manual_data.php` mit `period_id=998` und lokaler Zonennummer `relay`.

## Tests

```bash
PYTHONPATH=custom_components pytest tests/ -v
```

## Lizenz

Apache-2.0 — siehe [LICENSE](LICENSE).
