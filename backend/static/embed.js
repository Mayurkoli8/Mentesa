(function () {
  const scriptTag = document.currentScript;

  // --- Use optional backend URL ---
  const backend =
    scriptTag.getAttribute("data-backend-url") ||
    scriptTag.src.split("/static/embed.js")[0];
  const apiKey = scriptTag.getAttribute("data-api-key");
  const botName = scriptTag.getAttribute("data-bot-name") || "Mentesa Bot";

  // --- Chat widget ---
  const widget = document.createElement("div");
  widget.style.cssText = `
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 320px;
    height: 420px;
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 12px;
    display: none; /* hidden by default */
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 2px 15px rgba(0,0,0,0.25);
    z-index: 9999;
    font-family: Arial, sans-serif;
  `;

  const header = document.createElement("div");
  header.style.cssText =
    "background:#007bff; color:#fff; padding:10px; text-align:center; font-weight:bold;";
  header.textContent = botName;

  const messagesBox = document.createElement("div");
  messagesBox.style.cssText =
    "flex:1; overflow-y:auto; padding:10px; background:#f9f9f9;";

  const inputBox = document.createElement("div");
  inputBox.style.cssText =
    "display:flex; border-top:1px solid #ccc; background:#fff;";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Type a message...";
  input.style.cssText =
    "flex:1; padding:10px; border:none; outline:none; font-size:14px;";

  const sendBtn = document.createElement("button");
  sendBtn.innerText = "➤";
  sendBtn.style.cssText =
    "padding:10px 15px; border:none; cursor:pointer; background:#007bff; color:#fff; font-weight:bold;";

  inputBox.appendChild(input);
  inputBox.appendChild(sendBtn);
  widget.appendChild(header);
  widget.appendChild(messagesBox);
  widget.appendChild(inputBox);
  document.body.appendChild(widget);

  // --- Floating toggle button ---
  const toggleBtn = document.createElement("div");
  toggleBtn.innerHTML = "💬";
  toggleBtn.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 55px;
    height: 55px;
    background: #007bff;
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    z-index: 10000;
  `;
  document.body.appendChild(toggleBtn);

  // Toggle logic
  let isOpen = false;
  toggleBtn.onclick = () => {
    isOpen = !isOpen;
    widget.style.display = isOpen ? "flex" : "none";
  };

  // --- Helper functions ---
  function addMessage(sender, text) {
    const msg = document.createElement("div");
    msg.style.margin = "6px 0";
    msg.style.padding = "8px";
    msg.style.borderRadius = "8px";
    msg.style.maxWidth = "80%";
    msg.style.wordWrap = "break-word";
    msg.style.fontSize = "14px";

    if (sender === "You") {
      msg.style.background = "#007bff";
      msg.style.color = "#fff";
      msg.style.alignSelf = "flex-end";
    } else {
      msg.style.background = "#eaeaea";
      msg.style.color = "#000";
      msg.style.alignSelf = "flex-start";
    }

    msg.innerHTML = `<b style="font-size:12px;">${sender}:</b><br>${text}`;
    messagesBox.appendChild(msg);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addMessage("You", text);
    input.value = "";

    try {
      const res = await fetch(`${backend}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      addMessage(botName, data.reply || "No reply");
    } catch (err) {
      addMessage(botName, "Error: " + err.message);
    }
  }

  sendBtn.onclick = sendMessage;
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });
})();
