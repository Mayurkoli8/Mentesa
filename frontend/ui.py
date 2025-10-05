import streamlit as st
def show_header():
    """Display the Mentesa header with styling"""
    st.markdown("<h1 style='text-align:center; font-size:2.2rem; font-weight:700; margin-bottom:0.2em;'>Mentesa V7</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #888; font-size:1.1rem; margin-bottom:2em;'>Your professional multi-bot AI platform</p>", unsafe_allow_html=True)

def apply_custom_styles():
    st.markdown("""
<style>
.chat-scroll-box {
    max-height: 400px;
    min-height: 120px;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 12px;
    background: var(--background-color, #f8f9fa);
    border: 1px solid #e0e0e0;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    scroll-behavior: smooth;
    position: relative;
}

.chat-bubble-user {
    background: #dcf8c6;
    color: #222;
    padding: 0.7rem 1rem;
    border-radius: 12px 12px 4px 12px;
    margin: 0.5rem 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 1rem;
    word-wrap: break-word;
}
.chat-bubble-bot {
    background: #fff;
    color: #222;
    padding: 0.7rem 1rem;
    border-radius: 12px 12px 12px 4px;
    margin: 0.5rem 0;
    max-width: 80%;
    border: 1px solid #ececec;
    font-size: 1rem;
    word-wrap: break-word;
}
[data-theme="dark"] .chat-bubble-user {
    background: #2e4d2f;
    color: #e2e8f0;
}
[data-theme="dark"] .chat-bubble-bot {
    background: #232946;
    color: #e2e8f0;
    border: 1px solid #334155;
}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
    """, unsafe_allow_html=True)

# hide_header="""
#     <style>
#     footer {visibility: hidden;}
#     #MainMenu {visibility: hidden;}
#     header {visibility: hidden;}
#     </style>
# """
# st.markdown(hide_header, unsafe_allow_html=True)

import streamlit.components.v1 as components

def logo_animation():
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mentesa Animated Logo</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
    <style>
      body {
        margin: 0;
        background: transparent;
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* align to top */
        align-items: center;
        width: 100%;
        height: 100%;
        overflow: hidden;
        font-family: 'Orbitron', sans-serif;
      }
      #logo-container {
        width: 100%;
        max-width: 600px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        padding-top: -100px; /* adjust top space */
        margin-block-start: -50px;
      }
      #logo-text {
        margin-top: -50px;
        font-size: 5vw; /* responsive */
        min-font-size: 20px;
        max-font-size: 48px;
        opacity: 0;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #0ff, #8a2be2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 10px #0ff, 0 0 20px #8a2be2;
        transition: opacity 2s ease;
      }
      canvas {
        width: 100% !important;
        height: auto !important;
        display: block;
        margin-bottom: 0px; /* space before text */
      }
    </style>
    </head>
    <body>
    <div id="logo-container">
      <canvas id="network"></canvas>
      <div id="logo-text">Mentesa</div>
    </div>
    <script>
    const canvas = document.getElementById('network');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
        canvas.width = canvas.parentElement.offsetWidth;
        canvas.height = canvas.parentElement.offsetWidth * 0.5; // maintain aspect ratio
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const nodes = [];
    const maxNodes = 20;
    const radius = 6;
    const connections = [];

    for (let i = 0; i < maxNodes; i++) {
      nodes.push({
        x: Math.random() * canvas.width * 0.5 + canvas.width * 0.25,
        y: Math.random() * canvas.height * 0.5 + canvas.height * 0.25,
        alpha: 0
      });
    }

    for (let i = 0; i < maxNodes; i++) {
      for (let j = i + 1; j < maxNodes; j++) {
        if (Math.random() < 0.25) connections.push({i, j, alpha: 0});
      }
    }

    let nodeIndex = 0;
    let connIndex = 0;

    function animateNodes() {
      if (nodeIndex < nodes.length) {
        nodes[nodeIndex].alpha = 1;
        nodeIndex++;
        draw();
        setTimeout(animateNodes, 150);
      } else {
        setTimeout(animateConnections, 300);
      }
    }

    function animateConnections() {
      if (connIndex < connections.length) {
        connections[connIndex].alpha = 1;
        connIndex++;
        draw();
        setTimeout(animateConnections, 100);
      } else {
        document.getElementById('logo-text').style.opacity = 1;
      }
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      connections.forEach(conn => {
        const n1 = nodes[conn.i];
        const n2 = nodes[conn.j];
        ctx.beginPath();
        ctx.moveTo(n1.x, n1.y);
        ctx.lineTo(n2.x, n2.y);
        ctx.strokeStyle = `rgba(0, 255, 255, ${conn.alpha})`;
        ctx.lineWidth = 1.5;
        ctx.shadowColor = 'cyan';
        ctx.shadowBlur = 10;
        ctx.stroke();
      });

      nodes.forEach(node => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 255, 255, ${node.alpha})`;
        ctx.shadowColor = 'cyan';
        ctx.shadowBlur = 12;
        ctx.fill();
      });
    }

    animateNodes();
    </script>
    </body>
    </html>
    """
    # Increase height to avoid cutting
    components.html(html_code, height=250, width=700)