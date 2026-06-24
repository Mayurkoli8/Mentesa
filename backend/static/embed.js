(function () {
  const scriptTag = document.currentScript;

  const backend =
    scriptTag.getAttribute("data-backend-url") ||
    scriptTag.src.split("/static/embed.js")[0];
  const apiKey = scriptTag.getAttribute("data-api-key");
  const botName = scriptTag.getAttribute("data-bot-name") || "Mentesa Bot";
  const accent = scriptTag.getAttribute("data-accent") || "#00d9d9";
  const welcome =
    scriptTag.getAttribute("data-welcome") ||
    "Hi! 👋 How can I help you today?";

  // ---- Styles ----
  const style = document.createElement("style");
  style.textContent = `
    .mts-widget * { box-sizing: border-box; font-family: "Segoe UI", system-ui, sans-serif; }
    .mts-widget {
      position: fixed; bottom: 90px; right: 20px; width: 360px; height: 520px;
      max-height: calc(100vh - 120px); background: #fff; border-radius: 16px;
      display: flex; flex-direction: column; overflow: hidden;
      box-shadow: 0 12px 40px rgba(0,0,0,0.22); z-index: 2147483000;
      opacity: 0; transform: translateY(20px) scale(0.96);
      transition: opacity .25s ease, transform .25s cubic-bezier(.4,1.4,.5,1);
      pointer-events: none;
    }
    .mts-widget.open { opacity: 1; transform: translateY(0) scale(1); pointer-events: auto; }
    .mts-header {
      background: linear-gradient(135deg, ${accent}, #0a1320);
      color: #fff; padding: 16px 18px; display: flex; align-items: center; gap: 10px;
    }
    .mts-avatar {
      width: 36px; height: 36px; border-radius: 50%; background: rgba(255,255,255,.18);
      display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px;
    }
    .mts-title { font-weight: 700; font-size: 15px; line-height: 1.1; }
    .mts-status { font-size: 11px; opacity: .85; display: flex; align-items: center; gap: 5px; }
    .mts-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; display: inline-block; }
    .mts-close { margin-left: auto; cursor: pointer; opacity: .85; font-size: 20px; line-height: 1; background:none;border:none;color:#fff; }
    .mts-msgs { flex: 1; overflow-y: auto; padding: 16px; background: #f6f8fb; display: flex; flex-direction: column; gap: 10px; }
    .mts-row { display: flex; width: 100%; }
    .mts-bubble { padding: 10px 14px; border-radius: 16px; max-width: 78%; font-size: 14px; line-height: 1.45; word-wrap: break-word; animation: mtsIn .2s ease; }
    @keyframes mtsIn { from { opacity: 0; transform: translateY(6px);} to {opacity:1; transform:none;} }
    .mts-user { justify-content: flex-end; }
    .mts-user .mts-bubble { background: ${accent}; color: #06121f; border-bottom-right-radius: 4px; }
    .mts-bot .mts-bubble { background: #fff; color: #1a2332; border: 1px solid #e6eaf0; border-bottom-left-radius: 4px; }
    .mts-typing { display: flex; gap: 4px; padding: 12px 14px; }
    .mts-typing span { width: 7px; height: 7px; border-radius: 50%; background: #b8c2cf; animation: mtsBlink 1.2s infinite; }
    .mts-typing span:nth-child(2){ animation-delay: .2s; } .mts-typing span:nth-child(3){ animation-delay: .4s; }
    @keyframes mtsBlink { 0%,60%,100%{opacity:.3;} 30%{opacity:1;} }
    .mts-input { display: flex; gap: 8px; padding: 12px; background: #fff; border-top: 1px solid #eef1f5; }
    .mts-input input { flex: 1; padding: 12px 14px; border-radius: 22px; border: 1px solid #d8dee6; outline: none; font-size: 14px; }
    .mts-input input:focus { border-color: ${accent}; }
    .mts-send { width: 42px; height: 42px; border:none; border-radius: 50%; cursor: pointer; background: ${accent}; color: #06121f; font-size: 18px; flex-shrink: 0; transition: transform .15s; }
    .mts-send:hover { transform: scale(1.06); }
    .mts-foot { text-align: center; font-size: 11px; padding: 7px; color: #8a96a5; background: #fff; }
    .mts-foot a { color: ${accent}; text-decoration: none; }
    .mts-toggle {
      position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px;
      border-radius: 50%; background: linear-gradient(135deg, ${accent}, #0a1320);
      color: #fff; display: flex; align-items: center; justify-content: center;
      font-size: 26px; cursor: pointer; box-shadow: 0 6px 20px rgba(0,0,0,.25);
      z-index: 2147483000; transition: transform .2s; border:none;
    }
    .mts-toggle:hover { transform: scale(1.08) rotate(6deg); }
    @media (max-width: 440px){ .mts-widget{ width: calc(100vw - 24px); right: 12px; } }
  `;
  document.head.appendChild(style);

  // ---- Elements ----
  const widget = document.createElement("div");
  widget.className = "mts-widget";

  const initial = botName.trim().charAt(0).toUpperCase() || "M";
  widget.innerHTML = `
    <div class="mts-header">
      <div class="mts-avatar">${initial}</div>
      <div>
        <div class="mts-title">${botName}</div>
        <div class="mts-status"><span class="mts-dot"></span> Online</div>
      </div>
      <button class="mts-close" aria-label="Close">×</button>
    </div>
    <div class="mts-msgs"></div>
    <div class="mts-input">
      <input type="text" placeholder="Type a message..." />
      <button class="mts-send" aria-label="Send">➤</button>
    </div>
    <div class="mts-foot">Powered by <a href="https://mentesa-final.vercel.app" target="_blank">Mentesa</a></div>
  `;
  document.body.appendChild(widget);

  const toggleBtn = document.createElement("button");
  toggleBtn.className = "mts-toggle";
  toggleBtn.innerHTML = "💬";
  document.body.appendChild(toggleBtn);

  const messagesBox = widget.querySelector(".mts-msgs");
  const input = widget.querySelector("input");
  const sendBtn = widget.querySelector(".mts-send");
  const closeBtn = widget.querySelector(".mts-close");
  const footer = widget.querySelector(".mts-foot");

  let isOpen = false;
  let greeted = false;
  function toggle() {
    isOpen = !isOpen;
    widget.classList.toggle("open", isOpen);
    toggleBtn.innerHTML = isOpen ? "×" : "💬";
    if (isOpen && !greeted) {
      greeted = true;
      addMessage("bot", welcome);
      input.focus();
    }
  }
  toggleBtn.onclick = toggle;
  closeBtn.onclick = toggle;

  function addMessage(role, text) {
    const row = document.createElement("div");
    row.className = "mts-row " + (role === "user" ? "mts-user" : "mts-bot");
    const bubble = document.createElement("div");
    bubble.className = "mts-bubble";
    bubble.textContent = text;
    row.appendChild(bubble);
    messagesBox.appendChild(row);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return bubble;
  }

  function showTyping() {
    const row = document.createElement("div");
    row.className = "mts-row mts-bot";
    row.innerHTML = `<div class="mts-bubble mts-typing"><span></span><span></span><span></span></div>`;
    messagesBox.appendChild(row);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return row;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addMessage("user", text);
    input.value = "";
    const typing = showTyping();
    try {
      const res = await fetch(`${backend}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      typing.remove();
      if (!res.ok) {
        addMessage("bot", data.detail || "Sorry, something went wrong.");
      } else {
        addMessage("bot", data.reply || "No reply");
        if (data.branding === false && footer) footer.style.display = "none";
      }
    } catch (err) {
      typing.remove();
      addMessage("bot", "Connection error. Please try again.");
    }
  }

  sendBtn.onclick = sendMessage;
  input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });
})();
