(function () {
  const scriptTag = document.currentScript;

  const backend =
    scriptTag.getAttribute("data-backend-url") ||
    scriptTag.src.split("/static/embed.js")[0];
  const apiKey = scriptTag.getAttribute("data-api-key");

  // Attribute overrides (optional). Server config wins unless an attribute is set.
  const attr = {
    botName: scriptTag.getAttribute("data-bot-name"),
    accent: scriptTag.getAttribute("data-accent"),
    welcome: scriptTag.getAttribute("data-welcome"),
    position: scriptTag.getAttribute("data-position"),
    launcher: scriptTag.getAttribute("data-launcher"),
  };

  // Defaults; refined once /widget/config loads.
  let cfg = {
    accent: attr.accent || "#00d9d9",
    welcome: attr.welcome || "Hi! 👋 How can I help you today?",
    title: attr.botName || "Mentesa Bot",
    bot_name: attr.botName || "Mentesa Bot",
    position: attr.position || "right",
    launcher_icon: attr.launcher || "💬",
    branding: true,
  };

  // Pick black or white text for legibility on a given background color.
  function contrastText(hex) {
    if (!hex) return "#06121f";
    let c = hex.replace("#", "").trim();
    if (c.length === 3) c = c.split("").map((x) => x + x).join("");
    if (c.length !== 6) return "#06121f";
    const r = parseInt(c.slice(0, 2), 16);
    const g = parseInt(c.slice(2, 4), 16);
    const b = parseInt(c.slice(4, 6), 16);
    // Relative luminance (sRGB)
    const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return lum > 0.6 ? "#0a1320" : "#ffffff";
  }

  function injectStyles() {
    const side = cfg.position === "left" ? "left" : "right";
    const onAccent = contrastText(cfg.accent);
    const style = document.createElement("style");
    style.id = "mts-style";
    style.textContent = `
      .mts-widget * { box-sizing: border-box; font-family: "Segoe UI", system-ui, sans-serif; }
      .mts-widget {
        position: fixed; bottom: 90px; ${side}: 20px; width: 360px; height: 520px;
        max-height: calc(100vh - 120px); background: #ffffff; border-radius: 14px;
        display: flex; flex-direction: column; overflow: hidden;
        box-shadow: 0 12px 40px rgba(0,0,0,0.22); z-index: 2147483000;
        opacity: 0; transform: translateY(20px) scale(0.96);
        transition: opacity .25s ease, transform .25s cubic-bezier(.4,1.4,.5,1);
        pointer-events: none;
      }
      .mts-widget.open { opacity: 1; transform: translateY(0) scale(1); pointer-events: auto; }
      .mts-header {
        background: linear-gradient(135deg, ${cfg.accent}, #0a1320);
        color: #fff; padding: 16px 18px; display: flex; align-items: center; gap: 10px;
      }
      .mts-avatar {
        width: 36px; height: 36px; border-radius: 50%; background: rgba(255,255,255,.18);
        display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px;
      }
      .mts-title { font-weight: 700; font-size: 15px; line-height: 1.1; color:#fff; }
      .mts-status { font-size: 11px; opacity: .85; display: flex; align-items: center; gap: 5px; }
      .mts-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; display: inline-block; }
      .mts-close { margin-left: auto; cursor: pointer; opacity: .85; font-size: 20px; line-height: 1; background:none;border:none;color:#fff; }
      .mts-msgs { flex: 1; overflow-y: auto; padding: 16px; background: #f6f8fb; display: flex; flex-direction: column; gap: 10px; }
      .mts-row { display: flex; width: 100%; }
      .mts-bubble { padding: 10px 14px; border-radius: 14px; max-width: 78%; font-size: 14px; line-height: 1.45; word-wrap: break-word; animation: mtsIn .2s ease; }
      @keyframes mtsIn { from { opacity: 0; transform: translateY(6px);} to {opacity:1; transform:none;} }
      .mts-user { justify-content: flex-end; }
      .mts-user .mts-bubble { background: ${cfg.accent}; color: ${onAccent}; border-bottom-right-radius: 4px; }
      .mts-bot .mts-bubble { background: #fff; color: #1a2332; border: 1px solid #e6eaf0; border-bottom-left-radius: 4px; }
      .mts-typing { display: flex; gap: 4px; padding: 12px 14px; }
      .mts-typing span { width: 7px; height: 7px; border-radius: 50%; background: #b8c2cf; animation: mtsBlink 1.2s infinite; }
      .mts-typing span:nth-child(2){ animation-delay: .2s; } .mts-typing span:nth-child(3){ animation-delay: .4s; }
      @keyframes mtsBlink { 0%,60%,100%{opacity:.3;} 30%{opacity:1;} }
      .mts-input { display: flex; gap: 8px; padding: 12px; background: #fff; border-top: 1px solid #eef1f5; }
      .mts-input input {
        flex: 1; padding: 12px 14px; border-radius: 10px; border: 1px solid #d8dee6;
        outline: none; font-size: 14px; color: #1a2332; background: #ffffff;
      }
      .mts-input input::placeholder { color: #97a3b2; }
      .mts-input input:focus { border-color: ${cfg.accent}; }
      .mts-send { width: 42px; height: 42px; border:none; border-radius: 10px; cursor: pointer; background: ${cfg.accent}; color: ${onAccent}; font-size: 18px; flex-shrink: 0; transition: transform .15s; }
      .mts-send:hover { transform: scale(1.06); }
      .mts-foot { text-align: center; font-size: 11px; padding: 7px; color: #8a96a5; background: #fff; }
      .mts-foot a { color: ${cfg.accent}; text-decoration: none; }
      .mts-toggle {
        position: fixed; bottom: 20px; ${side}: 20px; width: 60px; height: 60px;
        border-radius: 50%; background: linear-gradient(135deg, ${cfg.accent}, #0a1320);
        color: #fff; display: flex; align-items: center; justify-content: center;
        font-size: 26px; cursor: pointer; box-shadow: 0 6px 20px rgba(0,0,0,.25);
        z-index: 2147483000; transition: transform .2s; border:none;
      }
      .mts-toggle:hover { transform: scale(1.08); }
      @media (max-width: 440px){ .mts-widget{ width: calc(100vw - 24px); ${side}: 12px; } }
    `;
    const existing = document.getElementById("mts-style");
    if (existing) existing.remove();
    document.head.appendChild(style);
  }

  let widget, toggleBtn, messagesBox, input, sendBtn, footer;

  function build() {
    injectStyles();

    widget = document.createElement("div");
    widget.className = "mts-widget";
    const initial = (cfg.title || "M").trim().charAt(0).toUpperCase() || "M";
    widget.innerHTML = `
      <div class="mts-header">
        <div class="mts-avatar">${initial}</div>
        <div>
          <div class="mts-title">${cfg.title}</div>
          <div class="mts-status"><span class="mts-dot"></span> Online</div>
        </div>
        <button class="mts-close" aria-label="Close">×</button>
      </div>
      <div class="mts-msgs"></div>
      <div class="mts-input">
        <input type="text" placeholder="Type a message..." aria-label="Message" />
        <button class="mts-send" aria-label="Send">➤</button>
      </div>
      <div class="mts-foot">Powered by <a href="https://www.mentesa.live" target="_blank" rel="noopener">Mentesa</a></div>
    `;
    document.body.appendChild(widget);

    toggleBtn = document.createElement("button");
    toggleBtn.className = "mts-toggle";
    toggleBtn.innerHTML = cfg.launcher_icon || "💬";
    toggleBtn.setAttribute("aria-label", "Open chat");
    document.body.appendChild(toggleBtn);

    messagesBox = widget.querySelector(".mts-msgs");
    input = widget.querySelector("input");
    sendBtn = widget.querySelector(".mts-send");
    footer = widget.querySelector(".mts-foot");

    if (cfg.branding === false && footer) footer.style.display = "none";

    toggleBtn.onclick = toggle;
    widget.querySelector(".mts-close").onclick = toggle;
    sendBtn.onclick = sendMessage;
    input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });
  }

  let isOpen = false;
  let greeted = false;
  function toggle() {
    isOpen = !isOpen;
    widget.classList.toggle("open", isOpen);
    toggleBtn.innerHTML = isOpen ? "×" : (cfg.launcher_icon || "💬");
    if (isOpen && !greeted) {
      greeted = true;
      addMessage("bot", cfg.welcome);
      input.focus();
    }
  }

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

  // Load server-side config (branding + customization) THEN build the widget.
  fetch(`${backend}/widget/config?api_key=${encodeURIComponent(apiKey || "")}`)
    .then((r) => (r.ok ? r.json() : null))
    .then((server) => {
      if (server) {
        // Server config is the source of truth; script attributes override it.
        cfg = {
          accent: attr.accent || server.accent || cfg.accent,
          welcome: attr.welcome || server.welcome || cfg.welcome,
          title: attr.botName || server.title || server.bot_name || cfg.title,
          bot_name: server.bot_name || cfg.bot_name,
          position: attr.position || server.position || cfg.position,
          launcher_icon: attr.launcher || server.launcher_icon || cfg.launcher_icon,
          branding: server.branding !== false,
        };
      }
    })
    .catch(() => {})
    .finally(build);
})();
