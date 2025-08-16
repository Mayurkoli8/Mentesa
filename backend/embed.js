// (function() {
//     // Read bot name and API key from the script tag
//     const scriptTag = document.currentScript;
//     const botName = scriptTag.getAttribute("data-bot-name") || "Mentesa Bot";
//     const apiKey = scriptTag.getAttribute("data-api-key");

//     // Create container
//     const container = document.createElement("div");
//     container.id = "mentesa-chat-widget";
//     container.style.position = "fixed";
//     container.style.bottom = "20px";
//     container.style.right = "20px";
//     container.style.width = "300px";
//     container.style.height = "400px";
//     container.style.border = "1px solid #ccc";
//     container.style.borderRadius = "12px";
//     container.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
//     container.style.backgroundColor = "#fff";
//     container.style.display = "flex";
//     container.style.flexDirection = "column";
//     container.style.overflow = "hidden";
//     container.style.zIndex = "99999";
//     container.style.fontFamily = "Arial, sans-serif";

//     // Header
//     const header = document.createElement("div");
//     header.style.backgroundColor = "#0084ff";
//     header.style.color = "white";
//     header.style.padding = "10px";
//     header.style.fontWeight = "bold";
//     header.style.textAlign = "center";
//     header.textContent = botName;
//     container.appendChild(header);

//     // Chat area
//     const chatArea = document.createElement("div");
//     chatArea.style.flex = "1";
//     chatArea.style.padding = "10px";
//     chatArea.style.overflowY = "auto";
//     chatArea.id = "mentesa-chat-area";
//     container.appendChild(chatArea);

//     // Footer input
//     const footer = document.createElement("div");
//     footer.style.padding = "10px";
//     footer.style.display = "flex";

//     const input = document.createElement("input");
//     input.type = "text";
//     input.placeholder = "Type your message…";
//     input.style.flex = "1";
//     input.style.padding = "8px";
//     input.style.borderRadius = "8px";
//     input.style.border = "1px solid #ccc";

//     const sendBtn = document.createElement("button");
//     sendBtn.textContent = "Send";
//     sendBtn.style.marginLeft = "8px";
//     sendBtn.style.padding = "8px 12px";
//     sendBtn.style.backgroundColor = "#0084ff";
//     sendBtn.style.color = "#fff";
//     sendBtn.style.border = "none";
//     sendBtn.style.borderRadius = "8px";
//     sendBtn.style.cursor = "pointer";

//     footer.appendChild(input);
//     footer.appendChild(sendBtn);
//     container.appendChild(footer);

//     // Powered by Mentesa
//     const footerLabel = document.createElement("div");
//     footerLabel.textContent = "Powered by Mentesa";
//     footerLabel.style.fontSize = "10px";
//     footerLabel.style.color = "#888";
//     footerLabel.style.textAlign = "center";
//     footerLabel.style.marginTop = "4px";
//     container.appendChild(footerLabel);

//     document.body.appendChild(container);

//     // Function to append messages
//     function appendMessage(sender, text) {
//         const msgDiv = document.createElement("div");
//         msgDiv.textContent = (sender === "user" ? "🧑 " : "🤖 ") + text;
//         msgDiv.style.marginBottom = "8px";
//         msgDiv.style.padding = "6px 10px";
//         msgDiv.style.borderRadius = "10px";
//         msgDiv.style.maxWidth = "80%";
//         msgDiv.style.wordWrap = "break-word";
//         msgDiv.style.backgroundColor = sender === "user" ? "#0084ff" : "#f1f0f0";
//         msgDiv.style.color = sender === "user" ? "#fff" : "#000";
//         msgDiv.style.alignSelf = sender === "user" ? "flex-end" : "flex-start";
//         chatArea.appendChild(msgDiv);
//         chatArea.scrollTop = chatArea.scrollHeight;
//     }

//     // Send message handler
//     sendBtn.addEventListener("click", () => {
//         const message = input.value.trim();
//         if (!message) return;
//         appendMessage("user", message);
//         input.value = "";

//         // Call backend API for bot reply
//         fetch(`${window.location.origin}/bots/reply`, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "Authorization": `Bearer ${apiKey}`
//             },
//             body: JSON.stringify({ message })
//         })
//         .then(res => res.json())
//         .then(data => {
//             if (data.reply) appendMessage("bot", data.reply);
//         })
//         .catch(err => appendMessage("bot", "⚠️ Error getting reply"));
//     });

//     // Send message on Enter
//     input.addEventListener("keypress", (e) => {
//         if (e.key === "Enter") sendBtn.click();
//     });
// })();
