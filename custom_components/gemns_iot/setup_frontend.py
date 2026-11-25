"""Register the Gemns setup dialog frontend module."""

from asyncio import Lock
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

DIALOG_MODULE_URL = "/gemns-setup-panel/dialog-scanner.js"
REGISTRATION_LOCK = "gemns_setup_frontend_registration_lock"
STATIC_PATH_REGISTERED = "gemns_setup_frontend_registered"


async def async_register_setup_frontend(hass: HomeAssistant) -> None:
    """Load the dialog module before the first Gemns entry exists."""
    if not await async_setup_component(hass, "frontend", {}):
        return

    registration_lock = hass.data.setdefault(REGISTRATION_LOCK, Lock())
    async with registration_lock:
        if hass.data.get(STATIC_PATH_REGISTERED):
            return
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    DIALOG_MODULE_URL,
                    str(Path(__file__).with_name("dialog-scanner.js")),
                    False,
                ),
            ]
        )
        frontend.add_extra_js_url(hass, DIALOG_MODULE_URL)
        hass.data[STATIC_PATH_REGISTERED] = True
