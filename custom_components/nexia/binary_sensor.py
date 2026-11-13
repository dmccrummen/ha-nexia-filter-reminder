"""Support for Nexia / Trane XL Thermostats."""

from typing import override

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import NexiaThermostatEntity
from .filter_reminder import (
    get_filter_reminder_frequency_months,
    get_filter_reminders_enabled,
    get_filter_size,
    has_active_filter_reminder,
    has_filter_reminder_support,
)
from .types import NexiaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: NexiaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for a Nexia device."""
    coordinator = config_entry.runtime_data
    nexia_home = coordinator.nexia_home

    entities = []
    for thermostat_id in nexia_home.get_thermostat_ids():
        thermostat = nexia_home.get_thermostat_by_id(thermostat_id)
        entities.append(
            NexiaBinarySensor(
                coordinator, thermostat, "is_blower_active", "blower_active"
            )
        )
        if thermostat.has_emergency_heat():
            entities.append(
                NexiaBinarySensor(
                    coordinator,
                    thermostat,
                    "is_emergency_heat_active",
                    "emergency_heat_active",
                )
            )

        if has_filter_reminder_support(thermostat):
            entities.append(NexiaFilterReminderBinarySensor(coordinator, thermostat))

    async_add_entities(entities)


class NexiaBinarySensor(NexiaThermostatEntity, BinarySensorEntity):
    """Provides Nexia BinarySensor support."""

    def __init__(self, coordinator, thermostat, sensor_call, translation_key):
        """Initialize the nexia sensor."""
        super().__init__(
            coordinator,
            thermostat,
            unique_id=f"{thermostat.thermostat_id}_{sensor_call}",
        )
        self._call = sensor_call
        self._state = None
        self._attr_translation_key = translation_key

    @property
    @override
    def is_on(self) -> bool:
        """Return the status of the sensor."""
        return getattr(self._thermostat, self._call)()


class NexiaFilterReminderBinarySensor(NexiaThermostatEntity, BinarySensorEntity):
    """On when the thermostat has an active filter change reminder."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "filter_reminder"

    def __init__(self, coordinator, thermostat):
        """Initialize the filter reminder sensor."""
        super().__init__(
            coordinator,
            thermostat,
            unique_id=f"{thermostat.thermostat_id}_filter_reminder",
        )

    @property
    @override
    def is_on(self) -> bool | None:
        """Return True if a filter reminder is active."""
        return has_active_filter_reminder(self._thermostat)

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the filter reminder settings."""
        return {
            "reminders_enabled": get_filter_reminders_enabled(self._thermostat),
            "frequency_months": get_filter_reminder_frequency_months(
                self._thermostat
            ),
            "filter_size": get_filter_size(self._thermostat),
        }
