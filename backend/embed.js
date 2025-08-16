document.addEventListener("DOMContentLoaded", function() {
    const botName = document.currentScript.getAttribute("data-bot-name") || "Mentesa Bot";
    const apiKey = document.currentScript.getAttribute("data-api-key") || "";

    // Create main container
    const chatBox = document.createElement("div");
    chatBox.id = "mentesa-chat-widget";
    chatBox.style.position = "fixed";
    chatBox.style.bottom = "20px";
    chatBox.style.right = "20px";
    chatBox.style.width = "300px";
    chatBox.style.height = "400px";
    chatBox.style.backgroundColor = "#fff";
    chatBox.style.border = "1px solid #ccc";
    chatBox.style.borderRadius = "12px";
    chatBox.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
    chatBox.style.zIndex = "9999";
    chatBox.style.display = "flex";
    chatBox.style.flexDirection = "column";
    chatBox.style.overflow = "hidden";

    // Header
    const header = document.createElement("div");
    header.style.backgroundColor = "#0084ff";
    header.style.color = "#fff";
    header.style.padding = "10px";
    header.style.fontWeight = "bold";
    header.style.textAlign = "center";
    header.textContent = botName + " (powered by Mentesa)";
    chatBox.appendChild(header);

    // Chat content
    const chatContent = document.createElement("div");
    chatContent.id = "mentesa-chat-content";
    chatContent.style.flex = "1";
    chatContent.style.padding = "10px";
    chatContent.style.overflowY = "auto";
    chatContent.style.backgroundColor = "#f9f9f9";
    chatBox.appendChild(chatContent);

    // Input container
    const inputContainer = document.createElement("div");
    inputContainer.style.display = "flex";
    inputContainer.style.borderTop = "1px solid #ccc";

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Type a message…";
    input.style.flex = "1";
    input.style.padding = "10px";
    input.style.border = "none";
    input.style.outline = "none";

    const sendBtn = document.createElement("button");
    sendBtn.textContent = "Send";
    sendBtn.style.backgroundColor = "#0084ff";
    sendBtn.style.color = "#fff";
    sendBtn.style.border = "none";
    sendBtn.style.padding = "0 15px";
    sendBtn.style.cursor = "pointer";

    inputContainer.appendChild(input);
    inputContainer.appendChild(sendBtn);
    chatBox.appendChild(inputContainer);

    document.body.appendChild(chatBox);

    // Dummy send function
    sendBtn.addEventListener("click", function() {
        const message = input.value.trim();
        if (!message) return;

        const userMsg = document.createElement("div");
        userMsg.textContent = "🧑 " + message;
        userMsg.style.backgroundColor = "#0084ff";
        userMsg.style.color = "#fff";
        userMsg.style.padding = "6px 10px";
        userMsg.style.margin = "5px 0";
        userMsg.style.borderRadius = "10px";
        userMsg.style.textAlign = "right";

        chatContent.appendChild(userMsg);
        chatContent.scrollTop = chatContent.scrollHeight;
        input.value = "";

        // Placeholder bot reply
        const botMsg = document.createElement("div");
        botMsg.textContent = "🤖 This is a reply from " + botName;
        botMsg.style.backgroundColor = "#f1f0f0";
        botMsg.style.color = "#000";
        botMsg.style.padding = "6px 10px";
        botMsg.style.margin = "5px 0";
        botMsg.style.borderRadius = "10px";
        botMsg.style.textAlign = "left";

        setTimeout(() => {
            chatContent.appendChild(botMsg);
            chatContent.scrollTop = chatContent.scrollHeight;
        }, 500);
    });
});
