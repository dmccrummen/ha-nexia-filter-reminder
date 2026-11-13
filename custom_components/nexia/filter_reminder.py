"""Helpers for reading Trane/Nexia filter reminder data.

The nexia library (2.13.0) keeps the full thermostat JSON from the cloud
but does not expose the filter reminder fields. These helpers read them
directly from that JSON. This module deliberately has no Home Assistant
imports so it can be tested on its own.

Relevant JSON (from the thermostat's "features" and "settings" lists):

    features: {"name": "filter_reminders",
               "has_active_reminder": true,
               "actions": {"dismiss": {"method": "POST",
                                       "href": ".../acknowledge_filter_reminder"}}}
    settings: {"type": "filter_reminders_enabled", "current_value": true}
              {"type": "filter_reminders_frequency", "current_value": 1}  # months
              {"type": "filter_size", "current_value": "20x25x1"}
"""

from __future__ import annotations

from typing import Any

FEATURE_FILTER_REMINDERS = "filter_reminders"
SETTING_ENABLED = "filter_reminders_enabled"
SETTING_FREQUENCY = "filter_reminders_frequency"
SETTING_SIZE = "filter_size"


def _thermostat_json(thermostat: Any) -> dict[str, Any]:
    """Return the raw thermostat JSON held by the nexia library."""
    data = getattr(thermostat, "_thermostat_json", None)
    return data if isinstance(data, dict) else {}


def get_filter_feature(thermostat: Any) -> dict[str, Any] | None:
    """Return the filter_reminders feature block, or None if not present."""
    for feature in _thermostat_json(thermostat).get("features") or []:
        if isinstance(feature, dict) and feature.get("name") == FEATURE_FILTER_REMINDERS:
            return feature
    return None


def get_setting_block(thermostat: Any, setting_type: str) -> dict[str, Any] | None:
    """Return a whole settings block (current value, options, update URL)."""
    for setting in _thermostat_json(thermostat).get("settings") or []:
        if isinstance(setting, dict) and setting.get("type") == setting_type:
            return setting
    return None


def _get_setting(thermostat: Any, setting_type: str) -> Any:
    setting = get_setting_block(thermostat, setting_type)
    return None if setting is None else setting.get("current_value")


def get_setting_options(thermostat: Any, setting_type: str) -> list[tuple[str, Any]]:
    """Return [(label, value), ...] for a settings block."""
    setting = get_setting_block(thermostat, setting_type) or {}
    return [
        (str(opt.get("label")), opt.get("value"))
        for opt in setting.get("options") or []
        if isinstance(opt, dict) and "value" in opt
    ]


def get_setting_url(thermostat: Any, setting_type: str) -> str | None:
    """Return the URL used to change a settings block."""
    setting = get_setting_block(thermostat, setting_type) or {}
    return ((setting.get("_links") or {}).get("self") or {}).get("href")


def has_filter_reminder_support(thermostat: Any) -> bool:
    """Return True if the cloud reports filter reminder data for this thermostat."""
    return get_filter_feature(thermostat) is not None


def has_active_filter_reminder(thermostat: Any) -> bool | None:
    """Return True if a filter reminder is currently active."""
    feature = get_filter_feature(thermostat)
    if feature is None:
        return None
    value = feature.get("has_active_reminder")
    return bool(value) if value is not None else None


def get_filter_dismiss_url(thermostat: Any) -> tuple[str, str] | None:
    """Return (method, href) for the "Filter Changed" action, if available."""
    feature = get_filter_feature(thermostat)
    if feature is None:
        return None
    dismiss = (feature.get("actions") or {}).get("dismiss") or {}
    href = dismiss.get("href")
    if not href:
        return None
    return (dismiss.get("method") or "POST").upper(), href


def get_filter_reminders_enabled(thermostat: Any) -> bool | None:
    """Return whether filter reminders are turned on."""
    value = _get_setting(thermostat, SETTING_ENABLED)
    return None if value is None else bool(value)


def get_filter_reminder_frequency_months(thermostat: Any) -> int | None:
    """Return the reminder frequency in months."""
    value = _get_setting(thermostat, SETTING_FREQUENCY)
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def get_filter_size(thermostat: Any) -> str | None:
    """Return the configured filter size, e.g. 20x25x1."""
    value = _get_setting(thermostat, SETTING_SIZE)
    return str(value) if value is not None else None


def get_current_option_label(thermostat: Any, setting_type: str) -> str | None:
    """Return the label of the currently selected option."""
    current = _get_setting(thermostat, setting_type)
    for label, value in get_setting_options(thermostat, setting_type):
        if value == current:
            return label
    return None
