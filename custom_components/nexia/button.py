"""Button entities for Nexia / Trane thermostats."""

from typing import override

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import NexiaThermostatEntity
from .filter_api import async_send_filter_request
from .filter_reminder import get_filter_dismiss_url, has_filter_reminder_support
from .types import NexiaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: NexiaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up buttons for a Nexia device."""
    coordinator = config_entry.runtime_data
    nexia_home = coordinator.nexia_home

    async_add_entities(
        NexiaFilterChangedButton(coordinator, thermostat)
        for thermostat_id in nexia_home.get_thermostat_ids()
        if has_filter_reminder_support(
            thermostat := nexia_home.get_thermostat_by_id(thermostat_id)
        )
    )


class NexiaFilterChangedButton(NexiaThermostatEntity, ButtonEntity):
    """Tell Trane the filter was changed (same as "Filter Changed" in the app)."""

    _attr_translation_key = "filter_changed"

    def __init__(self, coordinator, thermostat):
        """Initialize the button."""
        super().__init__(
            coordinator,
            thermostat,
            unique_id=f"{thermostat.thermostat_id}_filter_changed",
        )

    @override
    async def async_press(self) -> None:
        """Acknowledge the filter reminder in the Nexia/Trane cloud."""
        action = get_filter_dismiss_url(self._thermostat)
        if action is None:
            raise HomeAssistantError(
                "The Trane cloud did not provide a filter reminder reset action"
            )
        method, url = action
        if await async_send_filter_request(
            self.coordinator, self._thermostat, url, {}, method
        ):
            self._signal_thermostat_update()
