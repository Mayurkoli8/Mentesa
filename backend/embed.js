(function() {
  // Get the script tag that loaded this script
  const scriptTag = document.currentScript;

  // Read attributes
  const apiKey = scriptTag.dataset.apiKey || '';
  const botName = scriptTag.datasetBotName || 'Chat Bot';
  const accentColor = scriptTag.datasetAccentColor || '#0084ff';
  const width = scriptTag.datasetWidth || '300px';
  const height = scriptTag.datasetHeight || '400px';

  // Create main widget container
  const widget = document.createElement('div');
  widget.id = 'mentesa-widget';
  widget.style.width = width;
  widget.style.height = height;
  widget.style.borderRadius = '12px';
  widget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
  widget.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
  widget.style.overflow = 'hidden';
  widget.style.display = 'flex';
  widget.style.flexDirection = 'column';
  widget.style.backgroundColor = '#fff';

  // Header with bot name
  const header = document.createElement('div');
  header.innerText = botName;
  header.style.backgroundColor = accentColor;
  header.style.color = '#fff';
  header.style.textAlign = 'center';
  header.style.fontWeight = 'bold';
  header.style.padding = '10px';
  widget.appendChild(header);

  // Chat window
  const chatWindow = document.createElement('div');
  chatWindow.id = 'chat-window';
  chatWindow.style.flex = '1';
  chatWindow.style.padding = '10px';
  chatWindow.style.overflowY = 'auto';
  chatWindow.style.backgroundColor = '#f9f9f9';
  widget.appendChild(chatWindow);

  // Footer
  const footer = document.createElement('div');
  footer.innerText = 'Powered by Mentesa';
  footer.style.backgroundColor = '#f1f0f0';
  footer.style.color = '#555';
  footer.style.textAlign = 'center';
  footer.style.fontSize = '12px';
  footer.style.padding = '4px';
  widget.appendChild(footer);

  // Add widget to body
  document.body.appendChild(widget);

  // Minimal chat simulation (replace with real API call)
  function addMessage(role, text) {
    const msg = document.createElement('div');
    msg.innerText = (role === 'user' ? '🧑 ' : '🤖 ') + text;
    msg.style.marginBottom = '8px';
    msg.style.padding = '8px 12px';
    msg.style.borderRadius = '12px';
    msg.style.maxWidth = '70%';
    if (role === 'user') {
      msg.style.backgroundColor = accentColor;
      msg.style.color = '#fff';
      msg.style.marginLeft = 'auto';
      msg.style.textAlign = 'right';
    } else {
      msg.style.backgroundColor = '#f1f0f0';
      msg.style.color = '#000';
      msg.style.marginRight = 'auto';
      msg.style.textAlign = 'left';
    }
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  // Example welcome message
  addMessage('bot', `Hi! I'm ${botName}. How can I help you today?`);

})();
