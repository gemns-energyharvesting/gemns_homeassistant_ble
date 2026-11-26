# Gemns™ Home Assistant Integration

A comprehensive Home Assistant integration for managing Gemns™ battery-less BLE devices.

## Features

### 🔌 **BLE Support**
- **BLE (Bluetooth Low Energy)** - Automatic discovery modes
- **Using Home Assistant Built-in BLE Driver** - Uses built-in configuration of BLE from Home Assistant


## Installation

### Home Assistant Marketplace (2026.11 or later)

1. Sign in to Home Assistant as an administrator and open **Settings → Marketplace**. Review and accept the community-content notice if prompted.
2. Select **Add from link** in the upper-right corner.
3. If prompted to connect GitHub, select **Continue**, open the GitHub link, enter the displayed code, and approve the connection. Return to Home Assistant.
4. In **GitHub link**, enter `https://github.com/gemns-energyharvesting/gemns_homeassistant_ble` and select **Add**. If Marketplace asks for a **Type**, choose **Integration** and select **Add** again.
5. Open **Gemns IoT** in Marketplace. Select **Install**, review the version, and select **Install** again to confirm.
6. If the Gemns setup form opens, follow the steps below. If Home Assistant requests a restart, use **Settings → System → Repairs**, then open the setup form under **Settings → Devices & services**.

See the [official Home Assistant Marketplace guide](https://www.home-assistant.io/integrations/marketplace/#custom-repositories) for help adding a repository or connecting GitHub.

### Manual installation

1. Download the repository ZIP from GitHub and extract it.
2. Copy the repository’s `custom_components/gemns_iot` folder into Home Assistant’s `/config/custom_components/` directory and name the copied folder `gemns`. The resulting manifest path should be `/config/custom_components/gemns/manifest.json`.
3. Restart Home Assistant and follow the setup steps below.

## Set up a Gemns BLE device

1. Open **Settings → Devices & services**. If Gemns appears under **Discovered**, select **Add** on its card. Otherwise, select **Add integration** and search for **Gemns**.
2. Enter the **Network key** from the device label. In the Home Assistant Companion app, you can select **Scan QR code** to fill it in.
3. Choose the **Device type**. If several Bluetooth devices are listed, select yours. If Home Assistant hasn’t found the device and asks for its address, enter its Bluetooth MAC address.
4. Select **Submit**. If Home Assistant offers to assign an area, select one or choose **Skip and finish**.

A manually entered key contains exactly 16 decimal numbers from 0 to 255 with one space between each number. Example:

```text
0 17 34 51 68 85 102 119 136 153 170 187 204 221 238 255
```

## Device Status

### Status Types
- **Connected**: Device is actively communicating
- **Offline**: Device is not responding
- **Error**: Device has encountered an error

## Troubleshooting

### Common Issues

#### Integration Not Loading
- Check that all required files are in the correct directory
- Check Home Assistant logs for error messages

#### Devices Not Appearing
- Ensure BLE toggles are enabled
- Verify dongles are connected and responding

### Debug Mode
Enable debug logging in Home Assistant:
```yaml
logger:
  default: info
  logs:
    custom_components.gemns_iot: debug
```

## Development

### Architecture
- **Device Manager**: Handles device discovery and management
- **Platform Entities**: Home Assistant entity implementations
- **Configuration Flow**: UI-based setup and configuration

### Adding New Device Types
1. Create new platform file (e.g., `fan.py`)
2. Implement required entity methods
3. Add to platform list in `__init__.py`
4. Update constants and translations

## Support

### Documentation
- [Home Assistant Integration Documentation](https://developers.home-assistant.io/)
- [Custom Component Development](https://developers.home-assistant.io/docs/creating_component_index/)

### Issues and Feature Requests
- Report bugs via GitHub issues
- Request new features through GitHub discussions
- Contribute improvements via pull requests

## License

This integration is licensed under the MIT License. See the LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release
- BLE support
- Multi-device type support
- UI-based configuration
- Device management interface
