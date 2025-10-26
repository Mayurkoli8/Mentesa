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
    background: #f5f5f5;
    border-radius: 12px;
    display: none; /* hidden by default */
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    z-index: 9999;
    font-family: "Segoe UI", Arial, sans-serif;
  `;

  const header = document.createElement("div");
  header.style.cssText =
    "background:rgb(14, 17, 23); color:#fff; padding:12px; text-align:center; font-weight:bold;";
  header.textContent = botName;

  const messagesBox = document.createElement("div");
  messagesBox.style.cssText = `
    flex:1; 
    overflow-y:auto; 
    padding:12px; 
    background:#f5f5f5;
    display:flex; 
    flex-direction:column;
    gap:8px;
  `;

  const inputBox = document.createElement("div");
  inputBox.style.cssText =
    "display:flex; border-top:0px solid #ddd; background:#f5f5f5; padding:6px;";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Type a message...";
  input.style.cssText =
    "flex:1; padding:16px; border-radius:20px; border:1px solid #ccc; outline:none; font-size:14px;";

  const sendBtn = document.createElement("button");
  sendBtn.innerText = "➤";
  sendBtn.style.cssText =
    "margin-left:6px; padding:0 16px; border:none; border-radius:50%; cursor:pointer; background:rgb(14, 17, 23); color:#fff; font-size:16px;";

const footer = document.createElement("div");
footer.style.cssText =
    "background:rgb(14, 17, 23); padding:5px 0px; color:#fff; text-align:center; font-size:12px;";
footer.innerHTML = `Powered by <a href="https://mentesa.live" target="_blank" style="color:cyan; text-decoration:none;"> Mentesa Family</a> | <a href="https://mentesav6.streamlit.app" target="_blank" style="color:cyan; text-decoration:none;">Privacy Policy</a>`;

  inputBox.appendChild(input);
  inputBox.appendChild(sendBtn);
  widget.appendChild(header);
  widget.appendChild(messagesBox);
  widget.appendChild(inputBox);
  widget.appendChild(footer);
  document.body.appendChild(widget);

  // --- Floating toggle button ---
  const toggleBtn = document.createElement("div");
  toggleBtn.innerHTML = '<img src="logo.png" style="width:80%; height:80%; object-fit:cover; border-radius:50%;" alt="Mentesa logo">';
  toggleBtn.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 55px;
    height: 55px;
    background: rgb(14, 17, 23);
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
    const msgWrapper = document.createElement("div");
    msgWrapper.style.display = "flex";
    msgWrapper.style.width = "100%";

    const msg = document.createElement("div");
    msg.style.padding = "10px 14px";
    msg.style.borderRadius = "18px";
    msg.style.maxWidth = "70%";
    msg.style.wordWrap = "break-word";
    msg.style.fontSize = "14px";
    msg.style.lineHeight = "1.4";

    if (sender === "You") {
      msgWrapper.style.justifyContent = "flex-end";
      msg.style.background = "rgb(14, 17, 23)";
      msg.style.color = "#fff";
      msg.style.borderBottomRightRadius = "4px";
    } else {
      msgWrapper.style.justifyContent = "flex-start";
      msg.style.background = "#e4e6eb";
      msg.style.color = "#000";
      msg.style.borderBottomLeftRadius = "4px";
    }

    msg.innerHTML = text;
    msgWrapper.appendChild(msg);
    messagesBox.appendChild(msgWrapper);
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