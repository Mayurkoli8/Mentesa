(function() {
  const scriptTag = document.currentScript;
  const backend = scriptTag.src.split("/embed.js")[0]; 
  const apiKey = scriptTag.getAttribute("data-api-key");
  const botName = scriptTag.getAttribute("data-bot-name") || "Mentesa Bot";

  // --- Create chat widget ---
  const widget = document.createElement("div");
  widget.style.position = "fixed";
  widget.style.bottom = "20px";
  widget.style.right = "20px";
  widget.style.width = "300px";
  widget.style.height = "400px";
  widget.style.background = "#fff";
  widget.style.border = "1px solid #ccc";
  widget.style.borderRadius = "12px";
  widget.style.display = "flex";
  widget.style.flexDirection = "column";
  widget.style.overflow = "hidden";
  widget.style.boxShadow = "0 2px 12px rgba(0,0,0,0.2)";
  widget.style.zIndex = "9999";

  const messagesBox = document.createElement("div");
  messagesBox.style.flex = "1";
  messagesBox.style.overflowY = "auto";
  messagesBox.style.padding = "10px";

  const inputBox = document.createElement("div");
  inputBox.style.display = "flex";
  inputBox.style.borderTop = "1px solid #ccc";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Type a message...";
  input.style.flex = "1";
  input.style.padding = "10px";
  input.style.border = "none";
  input.style.outline = "none";

  const sendBtn = document.createElement("button");
  sendBtn.innerText = "Send";
  sendBtn.style.padding = "10px";
  sendBtn.style.border = "none";
  sendBtn.style.cursor = "pointer";
  sendBtn.style.background = "#007bff";
  sendBtn.style.color = "#fff";

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
          // 🔑 Pass API key properly
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
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

})();
