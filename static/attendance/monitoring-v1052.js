(function () {
  "use strict";
  const url = window.MONITORING_LIVE_URL;
  if (!url) return;
  const byId = (id) => document.getElementById(id);
  const text = (id, value) => { const el = byId(id); if (el) el.textContent = value; };
  const esc = (value) => String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
  const empty = (message) => `<p class="empty-state">${esc(message)}</p>`;

  function renderAttention(items) {
    const el = byId("monitorAttention"); if (!el) return;
    if (!items.length) { el.innerHTML = empty("Tiada isu memerlukan tindakan."); return; }
    el.innerHTML = items.map(item => {
      const icon = item.severity === "danger" ? "!" : item.severity === "warning" ? "◷" : "i";
      return `<div class="monitor-row ${esc(item.severity)}"><span>${icon}</span><div><b>${esc(item.name)}</b><small>${esc(item.issue)} · ${esc(item.detail)}</small></div></div>`;
    }).join("");
  }
  function renderTimeline(items) {
    const el = byId("monitorTimeline"); if (!el) return;
    if (!items.length) { el.innerHTML = empty("Belum ada daftar masuk hari ini."); return; }
    el.innerHTML = items.map(item => `<div class="timeline-row"><time>${esc(item.time)}</time><span class="${item.late ? "late" : "present"}"></span><div><b>${esc(item.name)}</b><small>${esc(item.status)}</small></div></div>`).join("");
  }
  function renderPeople(id, items, message) {
    const el = byId(id); if (!el) return;
    el.innerHTML = items.length ? items.map(item => `<div class="simple-person"><b>${esc(item.name)}</b><small>${esc(item.detail)}</small></div>`).join("") : empty(message);
  }
  async function refresh() {
    try {
      const response = await fetch(url, {headers:{"X-Requested-With":"XMLHttpRequest"}, cache:"no-store"});
      if (!response.ok) return;
      const data = await response.json(); if (!data.ok) return;
      text("monitorTotal", data.total); text("monitorAttended", data.attended); text("monitorLate", data.late);
      text("monitorAbsent", data.absent); text("monitorLeave", data.on_leave); text("monitorDuty", data.on_duty);
      text("monitorRateText", `${data.percentage}%`); text("monitorBrief", data.daily_brief);
      text("monitorUpdated", data.updated_at); text("attentionCount", data.attention.length);
      text("leaveCount", data.on_leave); text("dutyCount", data.on_duty); text("noCheckoutCount", data.no_checkout);
      renderAttention(data.attention); renderTimeline(data.timeline);
      renderPeople("monitorLeaveList", data.leave_items, "Tiada staf bercuti hari ini.");
      renderPeople("monitorDutyList", data.duty_items, "Tiada tugas rasmi hari ini.");
    } catch (error) { console.debug("Monitoring refresh skipped", error); }
  }
  setInterval(refresh, 30000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
})();
