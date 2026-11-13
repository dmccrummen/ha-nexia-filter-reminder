"""Select entities for Nexia / Trane filter reminder settings."""

from typing import override

from nexia.thermostat import NexiaThermostat

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NexiaDataUpdateCoordinator
from .entity import NexiaThermostatEntity
from .filter_api import async_send_filter_request
from .filter_reminder import (
    SETTING_FREQUENCY,
    SETTING_SIZE,
    get_current_option_label,
    get_setting_options,
    get_setting_url,
)
from .types import NexiaConfigEntry

# setting type in the Trane JSON -> translation key
FILTER_SELECTS = {
    SETTING_FREQUENCY: "filter_reminder_frequency",
    SETTING_SIZE: "filter_size",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: NexiaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up selects for a Nexia device."""
    coordinator = config_entry.runtime_data
    nexia_home = coordinator.nexia_home
    entities: list[SelectEntity] = []
    for thermostat_id in nexia_home.get_thermostat_ids():
        thermostat: NexiaThermostat = nexia_home.get_thermostat_by_id(thermostat_id)
        for setting_type, key in FILTER_SELECTS.items():
            if get_setting_url(thermostat, setting_type) and get_setting_options(
                thermostat, setting_type
            ):
                entities.append(
                    NexiaFilterSettingSelect(coordinator, thermostat, setting_type, key)
                )
    async_add_entities(entities)


class NexiaFilterSettingSelect(NexiaThermostatEntity, SelectEntity):
    """A filter reminder setting that can be changed from Home Assistant."""

    def __init__(
        self,
        coordinator: NexiaDataUpdateCoordinator,
        thermostat: NexiaThermostat,
        setting_type: str,
        key: str,
    ) -> None:
        """Initialize the select."""
        super().__init__(
            coordinator,
            thermostat,
            unique_id=f"{thermostat.thermostat_id}_{setting_type}_select",
        )
        self._setting_type = setting_type
        self._attr_translation_key = key

    @property
    @override
    def options(self) -> list[str]:
        """Return the available options."""
        return [
            label for label, _ in get_setting_options(self._thermostat, self._setting_type)
        ]

    @property
    @override
    def current_option(self) -> str | None:
        """Return the current option."""
        return get_current_option_label(self._thermostat, self._setting_type)

    @override
    async def async_select_option(self, option: str) -> None:
        """Change the setting in the Trane cloud."""
        values = dict(get_setting_options(self._thermostat, self._setting_type))
        if option not in values:
            raise HomeAssistantError(f"Unknown option {option}")
        url = get_setting_url(self._thermostat, self._setting_type)
        if url is None:
            raise HomeAssistantError("Trane cloud did not provide a settings URL")
        if await async_send_filter_request(
            self.coordinator, self._thermostat, url, {"value": values[option]}
        ):
            self._signal_thermostat_update()
