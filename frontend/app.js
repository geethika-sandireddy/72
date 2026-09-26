// ---- Backend wiring -------------------------------------------------
// Override at runtime without editing this file: ?api=http://host:port
const params = new URLSearchParams(location.search);
const BACKEND_URL = params.get('api') || 'http://127.0.0.1:8000';
const POLL_MS = 6000;
const HORIZONS_LIST = [5, 15, 30, 60, 180];
const GRID_NY = 24, GRID_NX = 30;

let selectedHorizon = 30;
let latest = null;          // last successful /forecast response
let connected = false;
let selectedCellId = null;
let frame = 0;

const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2600);
}

function updateClock() {
  const d = new Date();
  $("#clock").textContent = d.toISOString().slice(11, 19) + " UTC";
}
setInterval(updateClock, 1000);
updateClock();

// ---- Synthetic radar field generator --------------------------------
// The backend expects a real georeferenced grid in live/replay mode, but in
// SYNTHETIC provenance it just needs *some* field to run the storm-cell
// tracker and forecast heads against. We simulate two drifting convective
// cells so the whole pipeline (detection -> LAD state -> forecast) has
// something to track, the same way app/ingestion.py's demo mode would.
function syntheticRadarField(t) {
  const field = Array.from({ length: GRID_NY }, () => new Array(GRID_NX).fill(12));
  const blobs = [
    { cx: 10 + 4 * Math.sin(t / 14), cy: 9 + 2 * Math.cos(t / 20), peak: 55, r: 3.2 },
    { cx: 20 - 3 * Math.sin(t / 18), cy: 15 + 3 * Math.cos(t / 11), peak: 44, r: 2.4 },
  ];
  for (let y = 0; y < GRID_NY; y++) {
    for (let x = 0; x < GRID_NX; x++) {
      let v = field[y][x];
      for (const b of blobs) {
        const d2 = (x - b.cx) ** 2 + (y - b.cy) ** 2;
        v += b.peak * Math.exp(-d2 / (2 * b.r * b.r));
      }
      field[y][x] = Math.round(v * 10) / 10;
    }
  }
  return field;
}

// ---- Networking -------------------------------------------------------
async function pollForecast() {
  frame++;
  const body = {
    provenance: "SYNTHETIC",
    district: "Patna",
    state: "Bihar",
    radar_field: syntheticRadarField(frame),
  };
  try {
    const res = await fetch(`${BACKEND_URL}/forecast`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    latest = data;
    setConnected(true);
    render(data);
  } catch (err) {
    setConnected(false);
  }
}

function setConnected(ok) {
  if (ok === connected) return;
  connected = ok;
  const state = $("#systemState");
  const badge = $("#provenanceBadge");
  if (ok) {
    state.innerHTML = '<i></i> SYSTEM NOMINAL';
    state.querySelector('i').style.background = 'var(--green)';
    badge.textContent = 'LIVE · SYNTHETIC FEED';
    toast(`Connected to backend at ${BACKEND_URL}`);
  } else {
    state.innerHTML = '<i></i> BACKEND UNREACHABLE';
    state.querySelector('i').style.background = 'var(--red)';
    badge.textContent = 'DEMO · OFFLINE';
    toast(`Can't reach backend at ${BACKEND_URL} — showing last known / demo values. Run "uvicorn app.service:app --reload" and refresh.`);
  }
}

// ---- Rendering ----------------------------------------------------------
function render(data) {
  $("#lastUpdate").textContent = "just now";
  $("#caseLabel").textContent = `CASE / ${data.case_id.toUpperCase()}`;

  renderCells(data);
  renderKpis(data);
  renderHealth(data.sensor_health);
  renderHorizonPanel(data);
  renderTimeline(data);
  renderReview(data);
}

function peakForCell(data) {
  // Highest lightning probability across horizons, for KPI + review logic
  let best = { h: 30, p: -1 };
  for (const h of HORIZONS_LIST) {
    const p = data.forecast[String(h)]?.lightning_probability ?? 0;
    if (p > best.p) best = { h, p };
  }
  return best;
}

function renderKpis(data) {
  $("#cellCount").textContent = String(data.storm_cells.length).padStart(2, "0");
  $("#cellCountNote").innerHTML = data.storm_cells.length
    ? `<em class="green">●</em> tracking stable`
    : `<em class="amber">●</em> no cells above 35 dBZ`;

  const peak = peakForCell(data);
  $("#peakLightning").textContent = Math.round(peak.p * 100) + "%";
  $("#peakLightningHorizon").textContent = `+${peak.h} min`;

  const stormProb = data.forecast[String(peak.h)]?.thunderstorm_probability ?? 0;
  const label = stormProb >= 0.7 ? "HIGH" : stormProb >= 0.4 ? "MODERATE" : "LOW";
  $("#peakStorm").textContent = label;
  $("#peakStormLocation").textContent = `${data.alert_context.district} · ${data.alert_context.state}`;

  const present = data.sensor_health.filter(s => s.status !== "MISSING").length;
  $("#dataCoverage").textContent = `${present} / ${data.sensor_health.length}`;
  $("#dataCoverageNote").innerHTML = `<em class="amber">●</em> ${data.provenance.toLowerCase()} radar field`;

  $("#modelState").textContent = connected ? "READY" : "STALE";
  $("#modelVersion").textContent = `latency ${data.latency_ms} ms · ${data.provenance.toLowerCase()}`;

  $("#ladPressure").textContent = data.lad_state.pressure.toFixed(2);
  $("#ladPressureBar").style.width = Math.min(100, data.lad_state.pressure * 40) + "%";
}

function renderHealth(sensorHealth) {
  const ready = sensorHealth.filter(s => s.status !== "MISSING").length;
  $("#healthScore").textContent = `${ready} / ${sensorHealth.length} ready`;
  sensorHealth.forEach(s => {
    const row = document.querySelector(`.source-row[data-source="${s.source}"]`);
    if (!row) return;
    const dot = row.querySelector(".source-dot");
    const status = row.querySelector(".status");
    const small = row.querySelector("small");
    const live = s.status !== "MISSING";
    dot.className = "source-dot " + (live ? "synthetic-dot" : "off-dot");
    status.className = "status " + (live ? "synthetic-text" : "off-text");
    status.textContent = s.status;
    small.textContent = live ? "present" : "no payload";
  });
}

function gridToPercent(cy, cx) {
  // Map grid indices onto the stylized India outline footprint in the map card
  const left = 35 + (cx / GRID_NX) * 42;
  const top = 12 + (cy / GRID_NY) * 66;
  return { left, top };
}

function renderCells(data) {
  const container = $("#stormMarkers");
  container.innerHTML = "";
  if (!data.storm_cells.length) {
    selectedCellId = null;
    $("#selectedCell").innerHTML = "— <span class=\"severity\">NO CELL</span>";
    return;
  }
  const sorted = [...data.storm_cells].sort((a, b) => b.max_reflectivity - a.max_reflectivity);
  if (!sorted.some(c => c.cell_id === selectedCellId)) selectedCellId = sorted[0].cell_id;

  sorted.forEach((cell) => {
    const { left, top } = gridToPercent(cell.centroid_y, cell.centroid_x);
    const severe = cell.max_reflectivity >= 50;
    const btn = document.createElement("button");
    btn.className = "storm-marker" + (severe ? "" : " secondary") + (cell.cell_id === selectedCellId ? " selected" : "");
    btn.style.left = left.toFixed(1) + "%";
    btn.style.top = top.toFixed(1) + "%";
    btn.dataset.cell = String(cell.cell_id);
    btn.innerHTML = `<span class="pulse"></span><b>C-${cell.cell_id}</b><small>${severe ? "HIGH" : "MOD"}</small>`;
    btn.addEventListener("click", () => {
      selectedCellId = cell.cell_id;
      if (latest) renderCells(latest);
      toast(`C-${cell.cell_id} selected · inspector updated`);
    });
    container.appendChild(btn);
  });

  renderInspector(sorted.find(c => c.cell_id === selectedCellId) || sorted[0]);
}

function renderInspector(cell) {
  const severe = cell.max_reflectivity >= 50;
  $("#selectedCell").innerHTML = `C-${cell.cell_id} <span class="severity ${severe ? "high" : ""}">${severe ? "HIGH" : "MOD"}</span>`;
  $("#cellIntensity").innerHTML = `${cell.max_reflectivity.toFixed(0)} <small>dBZ</small>`;
  const growth = cell.area_growth * 100;
  const gEl = $("#cellGrowth");
  gEl.textContent = (growth >= 0 ? "+" : "") + growth.toFixed(0) + "%";
  gEl.className = growth >= 0 ? "trend-up" : "trend-down";
  const dir = compassFromMotion(cell.motion_y, cell.motion_x);
  const speed = Math.hypot(cell.motion_y, cell.motion_x) * 8; // grid cells -> rough km/h for display
  $("#cellMotion").innerHTML = `${dir} <small>${speed.toFixed(0)} km/h</small>`;
  $("#cellArea").innerHTML = `${cell.area} <small>cells</small>`;
}

function compassFromMotion(dy, dx) {
  if (dy === 0 && dx === 0) return "STATIONARY";
  const angle = Math.atan2(-dy, dx) * 180 / Math.PI;
  const dirs = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"];
  const idx = Math.round(((angle + 360) % 360) / 45) % 8;
  return dirs[idx];
}

function renderHorizonPanel(data) {
  const d = data.forecast[String(selectedHorizon)];
  if (!d) return;
  $("#cellLightning").textContent = Math.round(d.lightning_probability * 100) + "%";
  $("#cellStorm").textContent = Math.round(d.thunderstorm_probability * 100) + "%";
  $("#lightningBar").style.width = Math.round(d.lightning_probability * 100) + "%";
  $("#stormBar").style.width = Math.round(d.thunderstorm_probability * 100) + "%";
}

function renderTimeline(data) {
  const xs = { 5: 0, 15: 140, 30: 280, 60: 420, 180: 560 };
  const toY = p => 220 - p * 170 - 20; // leave headroom + baseline like the original chart
  const cyanPts = HORIZONS_LIST.map(h => [xs[h], toY(data.forecast[String(h)]?.lightning_probability ?? 0)]);
  const amberPts = HORIZONS_LIST.map(h => [xs[h], toY(data.forecast[String(h)]?.thunderstorm_probability ?? 0)]);
  const line = pts => pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]} ${p[1].toFixed(1)}`).join(" ");
  const area = pts => `${line(pts)} L700 ${pts[pts.length - 1][1].toFixed(1)} L700 220 L0 220Z`;

  $("#lineCyan").setAttribute("d", line(cyanPts));
  $("#lineAmber").setAttribute("d", line(amberPts));
  $("#areaCyan").setAttribute("d", area(cyanPts));
  $("#areaAmber").setAttribute("d", area(amberPts));

  const idx = HORIZONS_LIST.indexOf(selectedHorizon);
  const sel = cyanPts[idx], selA = amberPts[idx];
  if (sel) { $("#pointCyan").setAttribute("cx", sel[0]); $("#pointCyan").setAttribute("cy", sel[1].toFixed(1)); }
  if (selA) { $("#pointAmber").setAttribute("cx", selA[0]); $("#pointAmber").setAttribute("cy", selA[1].toFixed(1)); }
}

function renderReview(data) {
  const peak = peakForCell(data);
  const stormProb = data.forecast[String(peak.h)]?.thunderstorm_probability ?? 0;
  const alertBox = $(".review-alert");
  if (stormProb >= 0.55 && data.storm_cells.length) {
    alertBox.style.display = "";
    alertBox.querySelector("b").textContent = "Suggested elevated-risk review";
    alertBox.querySelector("small").textContent = `C-${selectedCellId ?? "?"} · +${peak.h} min · ${data.alert_context.district}, ${data.alert_context.state}`;
  } else {
    alertBox.style.display = "none";
  }
}

// ---- User interactions --------------------------------------------------
$$('[data-horizon]').forEach(b => b.addEventListener('click', () => {
  selectedHorizon = Number(b.dataset.horizon);
  $$('[data-horizon]').forEach(x => x.classList.toggle("selected", Number(x.dataset.horizon) === selectedHorizon));
  if (latest) { renderHorizonPanel(latest); renderTimeline(latest); }
  toast(`Forecast horizon advanced to +${selectedHorizon} minutes`);
}));

$$('.tool').forEach(b => b.addEventListener('click', () => {
  $$('.tool').forEach(x => x.classList.remove('active'));
  b.classList.add('active');
  $("#fieldLabel").textContent = b.textContent.toUpperCase();
  toast(`${b.textContent} layer selected`);
}));

$$('.nav-item,[data-view]').forEach(b => b.addEventListener('click', () => {
  const view = b.dataset.view;
  if (view) toast(view === 'operations' ? 'Operations workspace active' : view === 'replay' ? 'Replay lab is ready for authorized cases' : 'Evidence log opened');
}));

$("#refreshBtn").addEventListener('click', () => { toast('Refreshing forecast…'); pollForecast(); });

[["#approveBtn", "Draft recorded for forecaster approval"], ["#editBtn", "Draft moved to edit / hold"], ["#dismissBtn", "Draft dismissed locally"]]
  .forEach(([id, msg]) => $(id).addEventListener('click', () => {
    toast(msg);
    $(".review-state").textContent = id === "#approveBtn" ? 'PENDING' : id === "#editBtn" ? 'EDIT / HOLD' : 'DISMISSED';
  }));

// ---- Boot -----------------------------------------------------------------
pollForecast();
setInterval(pollForecast, POLL_MS);
