# Nexia / American Standard / Trane — with filter reminders

A drop-in replacement for Home Assistant's built-in **Nexia/American Standard/Trane** integration. It adds the thermostat's **filter change reminder**, which the built-in integration doesn't expose. Everything else works the same as the built-in integration.

Based on the Home Assistant **2026.11.1** core integration (nexia library 2.13.0).

## What it adds

| Entity | What it does |
|---|---|
| **Filter reminder** (binary sensor) | **Problem** when a filter change reminder is active in the Trane Home / Nexia / American Standard Home app. |
| **Filter changed** (button) | Clears the reminder, the same as tapping "Filter Changed" in the app. |
| **Filter reminders** (switch) | Turns filter reminders on or off. |
| **Filter reminder frequency** (select) | Reminder interval, 1–6 months. |
| **Filter size** (select) | Filter size saved in your account. |

Changes made in Home Assistant are sent to the Trane/Nexia cloud, so they show up in the app and on the thermostat.

These entities are only created when the cloud reports filter reminder data for a thermostat. If you don't see them, your thermostat model may not support this through the cloud. Other models are untested, so please open an issue with your model.

**Limits:**
- The cloud reports whether a reminder is active, but not how many days are left.
- Once a reminder is dismissed, it can't be brought back. Turning reminders off and on, or changing the frequency, only changes the schedule.

## Install

### HACS (recommended)

1. In Home Assistant, open **HACS → ⋮ → Custom repositories**.
2. Add `https://github.com/dmccrummen/ha-nexia-filter-reminder` with the type **Integration**.
3. Find **Nexia/American Standard/Trane (with filter reminders)** in HACS and select **Download**.
4. Restart Home Assistant.

HACS will notify you when updates are available.

### Manual

1. Copy `custom_components/nexia` from this repo into your Home Assistant config folder. The result should be `/config/custom_components/nexia/manifest.json`.
2. Restart Home Assistant.

## Set up

**If you already use the built-in Nexia integration**, there's nothing else to do. This version takes over your existing setup after the restart, and your entities and history are kept. The filter entities appear on your thermostat's device page.

**If this is your first time setting it up:**

1. Go to **Settings → Devices & services → Add integration**.
2. Search for **Nexia/American Standard/Trane**.
3. Choose your brand (Nexia, American Standard Home, or Trane Home). Then enter the email and password you use for that app.

To confirm the custom version is running, go to **Settings → Devices & services → Nexia**. It should show **Custom integration that replaces a Core component**.

## Example automation

Replace `binary_sensor.my_thermostat_filter_reminder` and the `notify` action with your own:

```yaml
automation:
  - alias: HVAC filter reminder
    triggers:
      - trigger: state
        entity_id: binary_sensor.my_thermostat_filter_reminder
        to: "on"
    actions:
      - action: notify.notify
        data:
          title: Change the HVAC filter
          message: >
            Time to change the HVAC filter. Press "Filter changed" in Home Assistant when done.
```

## Troubleshooting

To turn on debug logging, add this to `configuration.yaml` and restart:

```yaml
logger:
  logs:
    custom_components.nexia: debug
    nexia: debug
```

If you open an issue, attach your logs. You can also attach the integration's diagnostics (**⋮ → Download diagnostics**). Look over the diagnostics file before posting it, because it includes device serial numbers.

## Uninstall

Remove the integration from HACS, or delete `/config/custom_components/nexia`. Then restart. Home Assistant goes back to the built-in integration, and the filter entities can be deleted.

## Credits

Built on the Home Assistant core `nexia` integration (maintained by @bdraco) and the [`nexia`](https://github.com/bdraco/nexia) Python library. This project is not affiliated with Trane Technologies.
