# Gemns™ Home Assistant Integration

A comprehensive Home Assistant integration for managing Gemns™ battery-less BLE devices.

## Features

### 🔌 **BLE Support**
- **BLE (Bluetooth Low Energy)** - Automatic discovery modes
- **Using Home Assistant Built-in BLE Driver** - Uses built-in configuration of BLE from Home Assistant


## Installation

### Option 1: HACS (Recommended)
1. Install [HACS](https://hacs.xyz/)
2. Add this repository as a custom repository
3. Install "Gemns IoT" integration
4. Restart Home Assistant

### Option 2: Manual Installation
1. Copy the `integration` folder to your `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Integrations**
4. Click **+ Add Integration** and search for "Gemns IoT"


## Usage

### Adding Devices

#### Automatic Discovery
- Devices are automatically discovered when connected to BLE dongles

#### Manual Device Addition
1. Go to **Settings** → **Devices & Services** → **Gemns IoT**
2. Click **Add Device**
3. Fill in the device information:
   - **Device ID**: Unique identifier
   - **Device Name**: Display name
   - **Category**: Sensor, Switch, Light, Door, or Toggle
   - **BLE Discovery Mode**: V1 Auto (for BLE devices)

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
