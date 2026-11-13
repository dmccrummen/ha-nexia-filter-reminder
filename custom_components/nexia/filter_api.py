"""Send filter reminder changes to the Trane/Nexia cloud."""

import logging
from typing import Any

import aiohttp
from nexia.thermostat import NexiaThermostat

from homeassistant.exceptions import HomeAssistantError

from .coordinator import NexiaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_send_filter_request(
    coordinator: NexiaDataUpdateCoordinator,
    thermostat: NexiaThermostat,
    url: str,
    payload: dict[str, Any],
    method: str = "POST",
) -> bool:
    """Send a request and apply the returned thermostat data.

    Returns True if the response contained full thermostat data that was
    applied immediately (callers should then signal a thermostat update).
    """
    nexia_home = coordinator.nexia_home
    call = nexia_home.put_url if method.upper() == "PUT" else nexia_home.post_url

    try:
        async with await call(url, payload) as response:
            if response.status >= 400:
                raise HomeAssistantError(
                    f"Trane cloud rejected the request (HTTP {response.status})"
                )
            result = None
            try:
                result = (await response.json(content_type=None)).get("result")
            except (ValueError, AttributeError, aiohttp.ContentTypeError):
                pass
    except (TimeoutError, aiohttp.ClientError) as err:
        raise HomeAssistantError(f"Error talking to Trane cloud: {err}") from err

    _LOGGER.debug("Sent %s to %s for %s", payload, url, thermostat.thermostat_id)

    applied = False
    if isinstance(result, dict) and "features" in result and "zones" in result:
        thermostat.update_thermostat_json(result)
        applied = True

    await coordinator.async_request_refresh()
    return applied
