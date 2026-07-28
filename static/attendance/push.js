(function () {
  const enableButton = document.getElementById("enablePush");
  const disableButton = document.getElementById("disablePush");
  const statusBox = document.getElementById("pushStatus");
  if (!enableButton || !statusBox) return;

  const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie("csrftoken");
  function getCookie(name) {
    return document.cookie.split(";").map(v => v.trim()).find(v => v.startsWith(name + "="))?.split("=").slice(1).join("=") || "";
  }
  function toUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const raw = atob(base64);
    return Uint8Array.from([...raw].map(ch => ch.charCodeAt(0)));
  }
  async function registration() {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) throw new Error("Pelayar ini tidak menyokong Web Push.");
    return navigator.serviceWorker.ready;
  }
  async function refreshStatus() {
    try {
      const reg = await registration();
      const sub = await reg.pushManager.getSubscription();
      statusBox.textContent = sub ? "✅ Push Notification aktif pada peranti ini." : "Push Notification belum diaktifkan pada peranti ini.";
    } catch (error) { statusBox.textContent = "⚠️ " + error.message; }
  }
  enableButton.addEventListener("click", async () => {
    enableButton.disabled = true;
    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") throw new Error("Kebenaran notifikasi tidak diberikan.");
      const reg = await registration();
      let sub = await reg.pushManager.getSubscription();
      if (!sub) {
        const keyData = await fetch("/push/public-key/").then(r => r.json());
        sub = await reg.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: toUint8Array(keyData.publicKey)});
      }
      const response = await fetch("/push/subscribe/", {method: "POST", headers: {"Content-Type": "application/json", "X-CSRFToken": csrf}, body: JSON.stringify(sub.toJSON())});
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Langganan gagal.");
      statusBox.textContent = "✅ " + result.message;
    } catch (error) { statusBox.textContent = "⚠️ " + error.message; }
    enableButton.disabled = false;
  });
  disableButton.addEventListener("click", async () => {
    try {
      const reg = await registration();
      const sub = await reg.pushManager.getSubscription();
      if (sub) {
        await fetch("/push/unsubscribe/", {method: "POST", headers: {"Content-Type": "application/json", "X-CSRFToken": csrf}, body: JSON.stringify({endpoint: sub.endpoint})});
        await sub.unsubscribe();
      }
      statusBox.textContent = "Push Notification telah dinyahaktifkan pada peranti ini.";
    } catch (error) { statusBox.textContent = "⚠️ " + error.message; }
  });
  refreshStatus();
})();
