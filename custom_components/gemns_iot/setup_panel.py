"""Register the bundled Gemns BLE setup panel."""

from asyncio import Lock
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

PANEL_PATH = "gemns-setup"
MODULE_URL = "/gemns-setup-panel/setup-panel.js"
DIALOG_MODULE_URL = "/gemns-setup-panel/dialog-scanner.js"
REGISTRATION_LOCK = "gemns_setup_panel_registration_lock"
STATIC_PATH_REGISTERED = "gemns_setup_panel_static_path_registered"


async def async_register_setup_panel(hass: HomeAssistant) -> None:
    """Make the panel available even before the first Gemns entry exists."""
    if not await async_setup_component(hass, "panel_custom", {}):
        return

    registration_lock = hass.data.setdefault(REGISTRATION_LOCK, Lock())
    async with registration_lock:
        if not hass.data.get(STATIC_PATH_REGISTERED):
            await hass.http.async_register_static_paths(
                [
                    StaticPathConfig(
                        MODULE_URL,
                        str(Path(__file__).with_name("setup-panel.js")),
                        False,
                    ),
                    StaticPathConfig(
                        DIALOG_MODULE_URL,
                        str(Path(__file__).with_name("dialog-scanner.js")),
                        False,
                    ),
                ]
            )
            frontend.add_extra_js_url(hass, DIALOG_MODULE_URL)
            hass.data[STATIC_PATH_REGISTERED] = True

        if frontend.async_panel_exists(hass, PANEL_PATH):
            return

        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_PATH,
            webcomponent_name="gemns-setup-panel",
            sidebar_title="Gemns BLE Setup",
            sidebar_icon="mdi:bluetooth",
            module_url=MODULE_URL,
            require_admin=True,
        )
