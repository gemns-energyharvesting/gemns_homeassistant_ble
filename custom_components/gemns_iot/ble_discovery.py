"""Identify Gemns BLE advertisements for setup."""

from homeassistant.components.bluetooth import BluetoothServiceInfo

from .const import BLE_COMPANY_ID
from .packet_parser import PACKET_LENGTH, GemnsPacket


def is_gemns_advertisement(info: BluetoothServiceInfo) -> bool:
    """Match a complete Gemns manufacturer payload with a valid CRC."""
    data = info.manufacturer_data.get(BLE_COMPANY_ID)
    return data is not None and len(data) == PACKET_LENGTH and GemnsPacket(data).validate_crc()


def advertisement_name(info: BluetoothServiceInfo) -> str:
    """Use the advertised name or a stable label derived from the address."""
    address = info.address.upper()
    if info.name and info.name.upper() != address:
        return info.name
    return f"Gemns {address.replace(':', '')[-6:]}"
