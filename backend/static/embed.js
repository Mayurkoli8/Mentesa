(function() {
  const scriptTag = document.currentScript;
  const backend = scriptTag.getAttribute("data-backend-url") || scriptTag.src.split("/embed.js")[0];
  const apiKey = scriptTag.getAttribute("data-api-key");
  const botName = scriptTag.getAttribute("data-bot-name") || "Mentesa Bot";

  // --- Create chat widget ---
  const widget = document.createElement("div");
  Object.assign(widget.style, {
    position: "fixed",
    bottom: "20px",
    right: "20px",
    width: "300px",
    height: "400px",
    background: "#fff",
    border: "1px solid #ccc",
    borderRadius: "12px",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    boxShadow: "0 2px 12px rgba(0,0,0,0.2)",
    zIndex: "9999"
  });

  const messagesBox = document.createElement("div");
  Object.assign(messagesBox.style, { flex: "1", overflowY: "auto", padding: "10px" });

  const inputBox = document.createElement("div");
  Object.assign(inputBox.style, { display: "flex", borderTop: "1px solid #ccc" });

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Type a message...";
  Object.assign(input.style, { flex: "1", padding: "10px", border: "none", outline: "none" });

  const sendBtn = document.createElement("button");
  sendBtn.innerText = "Send";
  Object.assign(sendBtn.style, { padding: "10px", border: "none", cursor: "pointer", background: "#007bff", color: "#fff" });

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

      let data;
      try {
        data = await res.json();
      } catch {
        addMessage(botName, "Invalid response from server");
        return;
      }

      if (!res.ok) {
        addMessage(botName, `Error: ${data.detail || res.statusText}`);
        return;
      }

      addMessage(botName, data.reply || "No reply");
    } catch (err) {
      addMessage(botName, "Error: " + err.message);
    }
  }

  sendBtn.onclick = sendMessage;
  input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });
})();
