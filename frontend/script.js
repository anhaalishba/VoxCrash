const API = "";

async function load() {
  const [summary, records] = await Promise.all([
    fetch(API + "/api/summary").then(r => r.json()),
    fetch(API + "/api/evidence").then(r => r.json()),
  ]);
  renderStats(summary, records.length);
  renderCards(records);
}

function renderStats(summary, total) {
  const el = document.getElementById("stats");
  el.innerHTML = `
    <div class="pill"><b>${total}</b><span>caught</span></div>
  `;
}

function renderCards(records) {
  const el = document.getElementById("content");
  if (!records.length) {
    el.innerHTML = `<div class="empty">No slip-ups yet. Start a call above to find one.</div>`;
    return;
  }

  el.innerHTML = records.map(cardHTML).join("");

  document.querySelectorAll(".card-head").forEach(head => {
    head.addEventListener("click", () => head.parentElement.classList.toggle("open"));
  });

  document.querySelectorAll(".replay-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      alert("Run it again with:\n\npython main.py run " + btn.dataset.strategy);
    });
  });
}

function cardHTML(r) {
  const sevClass = (r.severity || "").toLowerCase();
  const transcript = (r.transcript_window || []).map(t => `
    <div class="line ${t.speaker}">
      <div class="speaker">${t.speaker === "customer" ? "Caller" : "Hotel"}</div>
      <div>${escapeHTML(t.text)}</div>
    </div>
  `).join("") || "<div class='line'><div>No transcript for this moment.</div></div>";

  return `
    <div class="card">
      <div class="card-head">
        <div class="card-title">
          <span class="chev">▶</span>
          <span class="sev ${sevClass}">${r.severity}</span>
          <span class="invariant">${escapeHTML(r.description)}</span>
        </div>
        <div style="font-size:12px;color:var(--ink-soft)">${new Date(r.detected_at).toLocaleTimeString()}</div>
      </div>
      <div class="card-body">
        <div class="meta-row">
          <div class="meta-block">
            <h4>What it booked anyway</h4>
            <pre>${escapeHTML(JSON.stringify(r.tool_call_args, null, 2))}</pre>
          </div>
        </div>
        <div class="transcript">
          <h4>What happened</h4>
          ${transcript}
        </div>
        <button class="replay-btn" data-strategy="${r.attack_strategy}">Run it again</button>
      </div>
    </div>
  `;
}

function escapeHTML(s) {
  if (s === undefined || s === null) return "";
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ---------- Live Call ----------

let ws;
const callWindow = document.getElementById("callWindow");
const wsDot = document.getElementById("wsDot");
const wsLabel = document.getElementById("wsLabel");
const runBtn = document.getElementById("runBtn");
const liveViolation = document.getElementById("liveViolation");

// ---------- Custom dropdown ----------
const dropdown = document.getElementById("strategyDropdown");
const dropdownBtn = document.getElementById("dropdownBtn");
const dropdownMenu = document.getElementById("dropdownMenu");
const dropdownEmoji = document.getElementById("dropdownEmoji");
const dropdownLabel = document.getElementById("dropdownLabel");
let selectedStrategy = "consent_withdrawal";

dropdownBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  dropdown.classList.toggle("open");
});
document.addEventListener("click", () => dropdown.classList.remove("open"));

dropdownMenu.querySelectorAll(".dropdown-item").forEach(item => {
  item.addEventListener("click", () => {
    selectedStrategy = item.dataset.value;
    dropdownEmoji.textContent = item.dataset.emoji;
    dropdownLabel.textContent = item.querySelector(".opt-title").textContent;
    dropdownMenu.querySelectorAll(".dropdown-item").forEach(i => i.classList.remove("selected"));
    item.classList.add("selected");
    dropdown.classList.remove("open");
  });
});

function connectLive() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${proto}//${location.host}/ws/live`);
  ws.onopen = () => { wsDot.classList.add("on"); wsLabel.textContent = "connected"; };
  ws.onclose = () => { wsDot.classList.remove("on"); wsLabel.textContent = "reconnecting"; setTimeout(connectLive, 2000); };
  ws.onerror = () => ws.close();
  ws.onmessage = (msg) => handleLiveEvent(JSON.parse(msg.data));
}

function handleLiveEvent(event) {
  if (event.type === "start") {
    callWindow.innerHTML = "";
    liveViolation.classList.remove("show");
    runBtn.disabled = true;
    runBtn.textContent = "On a call…";
  } else if (event.type === "status") {
    addSysLine(event.text);
  } else if (event.type === "transcript") {
    addBubble(event.speaker, event.text);
  } else if (event.type === "tool_call") {
    addSysLine("Booking in progress…");
  } else if (event.type === "violation") {
    document.getElementById("liveViolationTitle").textContent = "Caught something";
    document.getElementById("liveViolationDesc").textContent = event.description;
    liveViolation.classList.add("show");
  } else if (event.type === "error") {
    addSysLine("Something went wrong: " + event.text);
  } else if (event.type === "done") {
    addSysLine(event.violation_count ? "Call ended — found a slip-up." : "Call ended — all good.");
    runBtn.disabled = false;
    runBtn.textContent = "Start call";
    load();
  }
}

function addBubble(speaker, text) {
  const placeholder = callWindow.querySelector(".placeholder");
  if (placeholder) placeholder.remove();
  const row = document.createElement("div");
  row.className = `bubble-row ${speaker}`;
  row.innerHTML = `<div class="bubble"><div class="who">${speaker === "target" ? "Hotel" : "Caller"}</div>${escapeHTML(text)}</div>`;
  callWindow.appendChild(row);
  callWindow.scrollTop = callWindow.scrollHeight;
}

function addSysLine(text) {
  const placeholder = callWindow.querySelector(".placeholder");
  if (placeholder) placeholder.remove();
  const div = document.createElement("div");
  div.className = "sysline";
  div.textContent = text;
  callWindow.appendChild(div);
  callWindow.scrollTop = callWindow.scrollHeight;
}

runBtn.addEventListener("click", async () => {
  runBtn.disabled = true;
  runBtn.textContent = "Starting…";
  const res = await fetch(`/api/run/${selectedStrategy}`, { method: "POST" }).then(r => r.json());
  if (res.error) {
    alert(res.error);
    runBtn.disabled = false;
    runBtn.textContent = "Start call";
  }
});

connectLive();
load();
