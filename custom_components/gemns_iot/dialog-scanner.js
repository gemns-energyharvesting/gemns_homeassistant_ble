const DIALOG_STEP = "step-flow-form";
const controlsByStep = new WeakMap();
let activeScan;

function sendToCompanion(message) {
  window.webkit?.messageHandlers?.externalBus?.postMessage(message);
  if (window.webkit?.messageHandlers?.externalBus) return;
  if (window.externalAppV2?.postMessage) {
    window.externalAppV2.postMessage(JSON.stringify({ type: "externalBus", payload: message }));
  } else {
    window.externalApp.externalBus(JSON.stringify(message));
  }
}

function hasCompanionBridge() {
  return Boolean(window.webkit?.messageHandlers?.externalBus?.postMessage ||
    window.externalAppV2?.postMessage || window.externalApp?.externalBus);
}

function extractNetworkKey(raw) {
  if (typeof raw !== "string") return;
  const fields = raw.split(",");
  const key = fields.length === 3 ? fields[1] : raw;
  if (/^[0-9]{1,3}( [0-9]{1,3}){15}(?![\s\S])/.test(key) &&
      key.split(" ").every((number) => Number(number) <= 255)) {
    return key;
  }
}

function finishScan(close) {
  if (!activeScan) return;
  const { receive, previous, button } = activeScan;
  activeScan = undefined;
  if (window.externalBus === receive) window.externalBus = previous;
  button.disabled = false;
  if (close) sendToCompanion({ id: -2, type: "bar_code/close" });
}

function scan(step, button, status) {
  if (activeScan) return;
  const previous = window.externalBus;
  const receive = (message) => {
    if (message.type !== "command" ||
        !["bar_code/scan_result", "bar_code/aborted"].includes(message.command)) {
      return previous?.call(window, message);
    }
    const scanned = message.command === "bar_code/scan_result";
    try {
      sendToCompanion({ id: message.id, type: "result", success: true, result: null });
      finishScan(scanned);
      if (!scanned) return;
      const key = ["qr_code", "unknown"].includes(message.payload?.format)
        ? extractNetworkKey(message.payload.rawValue)
        : undefined;
      const form = step.shadowRoot?.querySelector("ha-form");
      if (!key || !form || !step.isConnected) {
        status.textContent = "No valid Gemns network key was found in the QR code.";
        return;
      }
      form.dispatchEvent(new CustomEvent("value-changed", {
        detail: { value: { ...form.data, decryption_key: key } },
      }));
      status.textContent = "Network key filled from QR code.";
    } catch {
      finishScan(false);
      status.textContent = "Could not read the QR code. Enter the network key manually.";
    }
  };
  activeScan = { receive, previous, button, step };
  window.externalBus = receive;
  button.disabled = true;
  status.textContent = "";
  try {
    sendToCompanion({
      id: -1,
      type: "bar_code/scan",
      payload: {
        title: "Scan Gemns QR code",
        description: "Scan the QR code on your device label.",
        alternative_option_label: "Close scanner",
      },
    });
  } catch {
    finishScan(false);
    status.textContent = "The scanner is unavailable. Enter the network key manually.";
  }
}

function addControls(step) {
  if (step.step?.handler !== "gemns" || step.step.step_id !== "ble" ||
      !hasCompanionBridge()) return;
  const form = step.shadowRoot?.querySelector("ha-form");
  if (!form || controlsByStep.get(step)?.isConnected) return;

  const controls = document.createElement("div");
  const button = document.createElement("ha-button");
  const status = document.createElement("div");
  button.textContent = "Scan QR code";
  status.setAttribute("role", "status");
  button.addEventListener("click", () => scan(step, button, status));
  controls.append(button, status);
  form.before(controls);
  controlsByStep.set(step, controls);
}

function addToOpenDialogs(root) {
  for (const element of root.querySelectorAll("*")) {
    if (element.localName === DIALOG_STEP) addControls(element);
    else if (element.shadowRoot) addToOpenDialogs(element.shadowRoot);
  }
}

if (hasCompanionBridge()) {
  customElements.whenDefined(DIALOG_STEP).then((component) => {
    const updated = component.prototype.updated;
    const disconnected = component.prototype.disconnectedCallback;
    component.prototype.updated = function (...args) {
      updated.apply(this, args);
      addControls(this);
    };
    component.prototype.disconnectedCallback = function (...args) {
      try {
        if (activeScan?.step === this) finishScan(true);
      } finally {
        disconnected.apply(this, args);
      }
    };
    addToOpenDialogs(document);
  });
}
