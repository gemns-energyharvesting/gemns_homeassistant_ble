class GemnsSetupPanel extends HTMLElement {
  connectedCallback() {
    if (this.shadowRoot) return;
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>
        :host { display: block; padding: 24px; color: var(--primary-text-color); }
        form { display: grid; gap: 16px; max-width: 480px; }
        label { display: grid; gap: 6px; }
        input, select, button { font: inherit; padding: 8px; }
        .actions { display: flex; flex-wrap: wrap; gap: 8px; }
        p { margin: 0; }
        header { display: flex; align-items: center; justify-content: space-between; gap: 12px; max-width: 480px; }
      </style>
      <header>
        <h1>Gemns BLE setup</h1>
        <button type="button" id="close-setup">Close</button>
      </header>
      <form>
        <div id="device-address" hidden></div>
        <label>Device name <input name="device_name" placeholder="Use the detected device name"></label>
        <label>Device type
          <select name="device_type">
            <option value="1">Button</option>
            <option value="2">Vibration Monitor</option>
            <option value="3">Two Way Switch</option>
            <option value="4" selected>Leak Detector</option>
          </select>
        </label>
        <label>Network key
          <input name="decryption_key" type="text" required autocomplete="off" spellcheck="false"
            aria-describedby="key-hint">
        </label>
        <p id="key-hint">Enter the 16 decimal numbers from the device label, with a space between each number. For example: 0 17 115 132 16 34 51 68 85 102 119 136 153 170 187 204.</p>
        <div class="actions">
          <button type="button" id="scan">Scan QR code</button>
          <button type="button" id="close-scan" hidden>Close scanner</button>
          <button type="submit">Add device</button>
        </div>
        <p role="status" aria-live="polite"></p>
      </form>
    `;
    this.form = root.querySelector("form");
    this.key = this.form.elements.decryption_key;
    this.scanButton = root.querySelector("#scan");
    this.closeScanButton = root.querySelector("#close-scan");
    this.addressField = root.querySelector("#device-address");
    this.closeScanButton.addEventListener("click", () => {
      this.stopScan(true);
      this.status.textContent = "Scanner closed.";
    });
    this.closeSetupButton = root.querySelector("#close-setup");
    this.closeSetupButton.addEventListener("click", () => this.closeSetup());
    this.submitButton = root.querySelector('button[type="submit"]');
    this.status = root.querySelector('[role="status"]');
    this.scanButton.addEventListener("click", () => this.scan());
    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      void this.submit();
    });
  }

  disconnectedCallback() {
    this.stopScan(true);
    if (this.key) this.key.value = "";
  }

  closeSetup() {
    this.stopScan(true);
    this.key.value = "";
    window.location.replace("/config/integrations/dashboard");
  }

  validKey(value) {
    return /^[0-9]{1,3}( [0-9]{1,3}){15}(?![\s\S])/.test(value) &&
      value.split(" ").every((number) => Number(number) <= 255);
  }

  sendToApp(message) {
    if (window.externalAppV2?.postMessage) {
      window.externalAppV2.postMessage(JSON.stringify({ type: "externalBus", payload: message }));
    } else if (window.externalApp?.externalBus) {
      window.externalApp.externalBus(JSON.stringify(message));
    } else {
      window.webkit.messageHandlers.externalBus.postMessage(message);
    }
  }

  scan() {
    if (this.scanHandler) return;
    if (!window.externalAppV2?.postMessage && !window.externalApp?.externalBus &&
        !window.webkit?.messageHandlers?.externalBus) {
      this.status.textContent = "Open this panel in the Home Assistant Companion app to scan, or enter the key manually.";
      return;
    }

    const previousHandler = window.externalBus;
    this.previousHandler = previousHandler;
    this.scanHandler = (message) => {
      if (message.type !== "command" ||
          !["bar_code/scan_result", "bar_code/aborted"].includes(message.command)) {
        return previousHandler?.call(window, message);
      }

      this.sendToApp({ id: message.id, type: "result", success: true, result: null });
      const scanned = message.command === "bar_code/scan_result";
      this.stopScan(scanned);
      if (!scanned) {
        this.status.textContent = "Scan canceled. You can enter the key manually.";
        return;
      }

      const rawValue = message.payload?.rawValue;
      const fields = typeof rawValue === "string" ? rawValue.split(",") : [];
      const value = fields.length === 3 ? fields[1] : rawValue;
      if (!["qr_code", "unknown"].includes(message.payload?.format) ||
          typeof value !== "string" || !this.validKey(value)) {
        this.status.textContent = "This QR code must contain 16 decimal numbers separated by single spaces.";
        return;
      }

      this.key.value = value;
      this.status.textContent = "Key scanned. Select Add device to finish.";
    };
    window.externalBus = this.scanHandler;
    this.closeScanButton.hidden = false;
    try {
      this.sendToApp({
        id: -1,
        type: "bar_code/scan",
        payload: {
          title: "Scan Gemns QR code",
          description: "Scan the QR code containing your device network key.",
          alternative_option_label: "Close scanner",
        },
      });
    } catch {
      this.stopScan(false);
      this.status.textContent = "Scanner unavailable. Enter the key manually.";
    }
  }

  stopScan(close) {
    if (!this.scanHandler) return;
    if (window.externalBus === this.scanHandler) window.externalBus = this.previousHandler;
    this.scanHandler = undefined;
    this.closeScanButton.hidden = true;
    this.previousHandler = undefined;
    if (close) {
      try {
        this.sendToApp({ id: -2, type: "bar_code/close" });
      } catch {
        // The Companion app bridge can disappear when the panel closes.
      }
    }
  }

  showAddressField(field) {
    const label = document.createElement("label");
    label.textContent = field.options ? "Bluetooth device" : "Bluetooth MAC address";
    const control = document.createElement(field.options ? "select" : "input");
    control.name = "address";
    control.required = true;
    if (field.options) {
      control.add(new Option("Select a device", ""));
      for (const [address, name] of field.options) {
        control.add(new Option(name, address));
      }
    } else {
      control.placeholder = "AA:BB:CC:DD:EE:FF";
    }
    label.append(control);
    this.addressField.replaceChildren(label);
    this.addressField.hidden = false;
    return control;
  }

  async submit() {
    const key = this.key.value;
    if (!this.validKey(key)) {
      this.status.textContent = "Enter the 16 decimal numbers from the device label, with a space between each number. For example: 0 17 115 132 16 34 51 68 85 102 119 136 153 170 187 204.";
      this.key.focus();
      return;
    }

    const hass = this.hass;
    const path = "config/config_entries/flow";
    this.submitButton.disabled = true;
    this.scanButton.disabled = true;
    this.closeSetupButton.disabled = true;
    this.status.textContent = "Adding device…";
    let flowId;
    try {
      const flow = await hass.callApi("POST", path, { handler: "gemns" });
      flowId = flow.flow_id;
      if (flow.type !== "form" || flow.step_id !== "ble") {
        throw new Error("Unexpected setup step");
      }

      const field = flow.data_schema?.find((item) => item.name === "address");
      let address = this.form.elements.address?.value;
      if (field?.required && !address) {
        this.showAddressField(field).focus();
        this.status.textContent = "Choose a Bluetooth device or enter its MAC address.";
        return;
      }
      if (!address) address = field?.default;

      const result = await hass.callApi("POST", `${path}/${flowId}`, {
        ...(address && { address }),
        decryption_key: key,
        device_name: this.form.elements.device_name.value,
        device_type: this.form.elements.device_type.value,
      });
      if (result.type === "create_entry") {
        flowId = undefined;
        this.key.value = "";
        this.addressField.replaceChildren();
        this.addressField.hidden = true;
        this.closeSetup();
      } else if (result.type === "abort" && result.reason === "already_configured") {
        flowId = undefined;
        this.status.textContent = "This Bluetooth device is already configured.";
      } else {
        const updatedField = result.data_schema?.find((item) => item.name === "address");
        if (updatedField) this.showAddressField(updatedField);
        this.status.textContent = "Home Assistant could not add the device. Check the setup values and try again.";
      }
    } catch {
      this.status.textContent = "Could not finish setup. Check your Home Assistant connection and try again.";
    } finally {
      if (flowId) void hass.callApi("DELETE", `${path}/${flowId}`).catch(() => {});
      this.submitButton.disabled = false;
      this.scanButton.disabled = false;
      this.closeSetupButton.disabled = false;
    }
  }
}

customElements.define("gemns-setup-panel", GemnsSetupPanel);
