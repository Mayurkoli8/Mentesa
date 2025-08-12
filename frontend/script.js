// Backend base URL
const API = "http://127.0.0.1:8000";

// UI elements
const botsListEl = document.getElementById("botsList");
const botsEmptyEl = document.getElementById("botsEmpty");
const createForm = document.getElementById("createForm");
const nameInput = document.getElementById("name");
const personalityInput = document.getElementById("personality");
const configInput = document.getElementById("config");

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const chatTitle = document.getElementById("chatTitle");
const selectedBotMeta = document.getElementById("selectedBotMeta");

let bots = [];
let currentBot = null;

// Utility
function el(tag, cls, html){ const d = document.createElement(tag); if(cls) d.className = cls; if(html!==undefined) d.innerHTML = html; return d; }
function formatDate(iso){ try { return new Date(iso).toLocaleString(); } catch(e){ return iso; } }
function getReplyKey(data){ return data?.reply ?? data?.bot_reply ?? data?.response ?? data?.message ?? null; }

// Load bots from backend
async function loadBots(){
  botsListEl.innerHTML = "Loading...";
  try {
    const res = await fetch(`${API}/bots`);
    if(!res.ok) throw new Error(`Status ${res.status}`);
    bots = await res.json();
    renderBots();
  } catch(err) {
    botsListEl.innerHTML = `<div class="muted">Error loading bots: ${err.message}</div>`;
    console.error(err);
  }
}

function renderBots(){
  botsListEl.innerHTML = "";
  if(!bots || bots.length === 0){
    botsEmptyEl.style.display = "";
    return;
  }
  botsEmptyEl.style.display = "none";

  bots.forEach(bot => {
    const item = el("div", "bot-item");
    const meta = el("div", "bot-meta");
    meta.innerHTML = `<div class="bot-name">${escapeHtml(bot.name)}</div>
                      <div class="bot-personality">${escapeHtml(bot.personality || "-")}</div>
                      <div class="muted" style="font-size:12px;margin-top:6px">${formatDate(bot.created_at || bot.createdAt || "")}</div>`;

    const actions = el("div", "bot-actions");
    const chatBtn = el("button", "btn small", "Chat");
    const delBtn = el("button", "btn small danger", "Delete");

    chatBtn.onclick = () => openChat(bot);
    delBtn.onclick = () => deleteBot(bot.id);

    actions.appendChild(chatBtn);
    actions.appendChild(delBtn);

    item.appendChild(meta);
    item.appendChild(actions);
    botsListEl.appendChild(item);
  });
}

// Create bot handler
createForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = nameInput.value.trim();
  const personality = personalityInput.value.trim();
  let config = {};
  if(configInput.value.trim()){
    try { config = JSON.parse(configInput.value.trim()); }
    catch(e){ alert("Invalid JSON in config"); return; }
  }
  try {
    const res = await fetch(`${API}/bots`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ name, personality, config })
    });
    if(!res.ok) {
      const txt = await res.text();
      throw new Error(`${res.status} ${txt}`);
    }
    // Accept both styles: backend returns created bot or {message, bot}
    const data = await res.json();
    const created = data?.bot ?? data;
    nameInput.value = "";
    personalityInput.value = "";
    configInput.value = "";
    await loadBots();
    if(created && created.id){
      // auto-open chat with created bot
      const b = bots.find(x => x.id === created.id) ?? created;
      setTimeout(()=>openChat(b), 200);
    }
  } catch(err){
    console.error("Create bot failed:", err);
    alert("Failed to create bot: " + err.message);
  }
});

// Delete bot
async function deleteBot(id){
  if(!confirm("Delete this bot?")) return;
  try {
    const res = await fetch(`${API}/bots/${id}`, { method: "DELETE" });
    if(res.status !== 204 && !res.ok){
      const txt = await res.text();
      throw new Error(`${res.status} ${txt}`);
    }
    if(currentBot && currentBot.id === id) closeChat();
    await loadBots();
  } catch(err) {
    console.error("Delete error:", err);
    alert("Delete failed: " + err.message);
  }
}

// Chat functions
function openChat(bot){
  currentBot = bot;
  chatTitle.textContent = `Chat — ${bot.name}`;
  selectedBotMeta.textContent = `${bot.name} · ${bot.id}`;
  chatMessages.innerHTML = "";
  chatInput.focus();
}

function closeChat(){
  currentBot = null;
  chatTitle.textContent = "Chat";
  selectedBotMeta.textContent = "Select a bot to start";
  chatMessages.innerHTML = "";
}

// Append message
function appendMessage(side, text){
  const row = el("div", "msg-row");
  const bubble = el("div", side === "user" ? "msg-user" : "msg-bot", escapeHtml(text));
  row.appendChild(bubble);
  chatMessages.appendChild(row);
  // scroll
  const area = document.getElementById("chatArea");
  area.scrollTop = area.scrollHeight;
}

// Submit chat
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if(!text){ return; }
  if(!currentBot){ alert("Select a bot first"); return; }

  appendMessage("user", text);
  chatInput.value = "";
  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ bot_id: currentBot.id, message: text })
    });
    if(!res.ok){
      const txt = await res.text();
      throw new Error(`${res.status} ${txt}`);
    }
    const data = await res.json();
    const reply = getReplyKey(data) ?? "No reply";
    appendMessage("bot", reply);
  } catch(err) {
    console.error("Chat failed:", err);
    appendMessage("bot", "⚠️ Error: " + err.message);
  }
});

// Escape HTML to avoid XSS
function escapeHtml(s){
  if(s === null || s === undefined) return "";
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

// Init
loadBots();
