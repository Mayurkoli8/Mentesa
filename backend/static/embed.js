(function() {
  const scriptTag = document.currentScript;

  // --- Use optional backend URL ---
  const backend = scriptTag.getAttribute("data-backend-url") || scriptTag.src.split("/embed.js")[0];
  const apiKey = scriptTag.getAttribute("data-api-key");
  const botName = scriptTag.getAttribute("data-bot-name") || "Mentesa Bot";

  // --- Create widget ---
  const widget = document.createElement("div");
  widget.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 300px;
    height: 400px;
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    z-index: 9999;
  `;

  const messagesBox = document.createElement("div");
  messagesBox.style.cssText = "flex:1; overflow-y:auto; padding:10px;";
  const inputBox = document.createElement("div");
  inputBox.style.cssText = "display:flex; border-top:1px solid #ccc;";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Type a message...";
  input.style.cssText = "flex:1; padding:10px; border:none; outline:none;";

  const sendBtn = document.createElement("button");
  sendBtn.innerText = "Send";
  sendBtn.style.cssText = "padding:10px; border:none; cursor:pointer; background:#007bff; color:#fff;";

  inputBox.appendChild(input);
  inputBox.appendChild(sendBtn);
  widget.appendChild(messagesBox);
  widget.appendChild(inputBox);
  document.body.appendChild(widget);

  function addMessage(sender, text) {
    const msg = document.createElement("div");
    msg.style.margin = "5px 0";
    msg.innerHTML = `<b>${sender}:</b> ${text}`;
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
          "Authorization": `Bearer ${apiKey}`
        },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      addMessage(botName, data.reply || "No reply");
    } catch (err) {
      addMessage(botName, "Error: " + err.message);
    }
  }

  sendBtn.onclick = sendMessage;
  input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });
})();
