"""Config flow for Gemns™ IoT integration."""

import logging
import re
from typing import Any

import voluptuous as vol
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfo, async_discovered_service_info
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME, CONF_NAME, CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_MQTT_BROKER,
    CONF_MQTT_USERNAME,
    CONF_MQTT_PASSWORD,
    CONF_ENABLE_ZIGBEE,
    CONF_SCAN_INTERVAL,
    CONF_HEARTBEAT_INTERVAL,
    DEFAULT_MQTT_BROKER,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_HEARTBEAT_INTERVAL,
    DEFAULT_ENABLE_ZIGBEE,
    DOMAIN,
    CONF_DECRYPTION_KEY,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
)

from .ble_discovery import advertisement_name, is_gemns_advertisement
from .decryption_key import parse_decryption_key
from .setup_panel import async_register_setup_panel

_LOGGER = logging.getLogger(__name__)


class GemnsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gemns™ IoT."""

    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        pass

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # MQTT option temporarily disabled - firmware not developed yet
        # To re-enable MQTT: uncomment the integration_type selection below
        # and restore the conditional logic in the rest of this method
        
        # Force BLE manual provisioning for now
        await async_register_setup_panel(self.hass)
        return await self.async_step_ble()
        
        # MQTT OPTION (COMMENTED OUT - TO RE-ENABLE WHEN FIRMWARE IS READY):
        # if user_input is None:
        #     return self.async_show_form(
        #         step_id="user",
        #         data_schema=vol.Schema(
        #             {
        #                 vol.Required("integration_type"): vol.In({
        #                     "mqtt": "MQTT-based (Traditional)",
        #                     "ble": "Bluetooth Low Energy (BLE) - Manual Provisioning"
        #                 }),
        #             }
        #         ),
        #     )
        #
        # integration_type = user_input["integration_type"]
        # 
        # if integration_type == "ble":
        #     # Redirect to BLE config flow for automatic provisioning
        #     return await self.async_step_ble()
        # else:
        #     # Continue with MQTT setup
        #     return await self.async_step_mqtt()

    async def async_step_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle MQTT configuration step."""
        if user_input is None:
            return self.async_show_form(
                step_id="mqtt",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_MQTT_BROKER, default=DEFAULT_MQTT_BROKER
                        ): str,
                        vol.Optional(CONF_MQTT_USERNAME): str,
                        vol.Optional(CONF_MQTT_PASSWORD): str,
                        vol.Required(
                            CONF_ENABLE_ZIGBEE, default=DEFAULT_ENABLE_ZIGBEE
                        ): bool,
                        vol.Required(
                            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                        ): vol.Coerce(float),
                        vol.Required(
                            CONF_HEARTBEAT_INTERVAL, default=DEFAULT_HEARTBEAT_INTERVAL
                        ): vol.Coerce(float),
                    }
                ),
            )

        # Validate MQTT broker URL
        mqtt_broker = user_input[CONF_MQTT_BROKER]
        if not mqtt_broker.startswith(("mqtt://", "mqtts://")):
            return self.async_show_form(
                step_id="mqtt",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_MQTT_BROKER, default=mqtt_broker
                        ): str,
                        vol.Optional(CONF_MQTT_USERNAME): str,
                        vol.Optional(CONF_MQTT_PASSWORD): str,
                        vol.Required(
                            CONF_ENABLE_ZIGBEE, default=user_input[CONF_ENABLE_ZIGBEE]
                        ): bool,
                        vol.Required(
                            CONF_SCAN_INTERVAL, default=user_input[CONF_SCAN_INTERVAL]
                        ): vol.Coerce(float),
                        vol.Required(
                            CONF_HEARTBEAT_INTERVAL, default=user_input[CONF_HEARTBEAT_INTERVAL]
                        ): vol.Coerce(float),
                    }
                ),
                errors={"base": "invalid_mqtt_broker"},
            )

        # Create the config entry
        return self.async_create_entry(
            title="Gemns™ IoT (MQTT)",
            data={
                CONF_MQTT_BROKER: mqtt_broker,
                CONF_MQTT_USERNAME: user_input.get(CONF_MQTT_USERNAME, ""),
                CONF_MQTT_PASSWORD: user_input.get(CONF_MQTT_PASSWORD, ""),
                CONF_ENABLE_ZIGBEE: user_input[CONF_ENABLE_ZIGBEE],
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                CONF_HEARTBEAT_INTERVAL: user_input[CONF_HEARTBEAT_INTERVAL],
            },
        )

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfo) -> FlowResult:
        """Open setup for the device that triggered Bluetooth discovery."""
        if not is_gemns_advertisement(discovery_info):
            return self.async_abort(reason="not_supported")
        self._discovered_device = discovery_info
        await self.async_set_unique_id(discovery_info.address.upper())
        self._abort_if_unique_id_configured()
        self._async_abort_entries_match({CONF_ADDRESS: discovery_info.address.upper()})
        await async_register_setup_panel(self.hass)
        return await self.async_step_ble()

    async def async_step_ble(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Select a BLE device and save its network key."""
        discovered_device = getattr(self, "_discovered_device", None)
        devices = {}
        if discovered_device is not None:
            devices[discovered_device.address.upper()] = advertisement_name(discovered_device)
        else:
            devices = {
                info.address.upper(): advertisement_name(info)
                for info in async_discovered_service_info(self.hass, connectable=False)
                if is_gemns_advertisement(info)
            }
        address_options = {address: f"{name} ({address})" for address, name in devices.items()}
        errors = {}
        if user_input is not None:
            address = user_input.get(CONF_ADDRESS, "").strip().upper()
            if discovered_device is not None or (not address and len(devices) == 1):
                address = next(iter(devices))
            if not re.fullmatch(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}", address):
                errors[CONF_ADDRESS] = "invalid_ble_address"
            try:
                key_hex = parse_decryption_key(user_input[CONF_DECRYPTION_KEY])
            except ValueError:
                errors[CONF_DECRYPTION_KEY] = "invalid_decryption_key_format"

            if not errors:
                await self.async_set_unique_id(address, raise_on_progress=False)
                self._abort_if_unique_id_configured()
                self._async_abort_entries_match({CONF_ADDRESS: address})
                default_name = devices.get(address, f"Gemns {address.replace(':', '')[-6:]}")
                device_name = user_input.get(CONF_DEVICE_NAME) or default_name
                return self.async_create_entry(
                    title=device_name,
                    data={
                        CONF_NAME: default_name,
                        CONF_ADDRESS: address,
                        CONF_DECRYPTION_KEY: key_hex,
                        CONF_DEVICE_NAME: device_name,
                        CONF_DEVICE_TYPE: int(user_input[CONF_DEVICE_TYPE]),
                    },
                )

        schema = {
            vol.Required(CONF_DECRYPTION_KEY): TextSelector(TextSelectorConfig(autocomplete="off")),
            vol.Optional(CONF_DEVICE_NAME): str,
            vol.Required(CONF_DEVICE_TYPE): vol.In({
                "4": "Leak Detector",
                "1": "Button",
                "2": "Vibration Monitor",
                "3": "Two Way Switch",
            }),
        }
        if discovered_device is None:
            if len(devices) == 1:
                schema[vol.Optional(CONF_ADDRESS, default=next(iter(devices)))] = vol.In(address_options)
            elif devices:
                schema[vol.Required(CONF_ADDRESS)] = vol.In(address_options)
            else:
                schema[vol.Required(CONF_ADDRESS)] = str

        return self.async_show_form(step_id="ble", data_schema=vol.Schema(schema), errors=errors)


    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)

    async def async_step_add_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding a new device."""
        if user_input is None:
            return self.async_show_form(
                step_id="add_device",
                data_schema=vol.Schema(
                    {
                        vol.Required("device_id"): str,
                        vol.Required("device_type"): vol.In(["ble", "zigbee"]),
                        vol.Required("device_category"): vol.In(["sensor", "switch", "light", "door", "toggle"]),
                        vol.Required("ble_discovery_mode"): vol.In(["v0_manual", "v1_auto"]),
                        vol.Optional("device_name"): str,
                        vol.Optional("network_key"): str,
                    }
                ),
            )

        # Add device logic would go here
        # For now, just return to main flow
        return self.async_abort(reason="device_added")
