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

def logo_animation():
    import base64
    import streamlit.components.v1 as components

    # Load your logo as base64
    with open("frontend/logo.png", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Mentesa Particle Assemble Logo</title>
      <style>
        body {{
          margin: 0;
          background: transparent;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100%;
          overflow: hidden;
        }}
        #canvas {{
          width: 100%;
          max-width: 450px;
          height: auto;
          display: block;
        }}
      </style>
    </head>
    <body>
      <canvas id="canvas"></canvas>
      <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {{
          canvas.width = canvas.parentElement.offsetWidth;
          canvas.height = canvas.width * 0.9;
        }}
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const img = new Image();
        img.src = "data:image/png;base64,{img_base64}";
        const particles = [];
        const radius = 2;
        const maxParticles = 500;
        let formed = false;
        let startTime = null;

        // mouse object
        let mouse = {{x: null, y: null}};
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            // map to canvas coordinates
            mouse.x = (e.clientX - rect.left) * (canvas.width / rect.width);
            mouse.y = (e.clientY - rect.top) * (canvas.height / rect.height);
        }});
        canvas.addEventListener('mouseleave', () => {{
            mouse.x = null;
            mouse.y = null;
        }});

        img.onload = () => {{
          const iw = 220;
          const ih = 220;
          const tempCanvas = document.createElement('canvas');
          const tctx = tempCanvas.getContext('2d');
          tempCanvas.width = iw;
          tempCanvas.height = ih;
          tctx.drawImage(img, 0, 0, iw, ih);
          const data = tctx.getImageData(0, 0, iw, ih).data;
          const validPixels = [];

          for (let y = 0; y < ih; y += 2) {{
            for (let x = 0; x < iw; x += 2) {{
              const index = (y * iw + x) * 4;
              const a = data[index + 3];
              if (a > 150) validPixels.push({{x, y, index}});
            }}
          }}

          const chosen = [];
          while (chosen.length < maxParticles && validPixels.length) {{
            const i = Math.floor(Math.random() * validPixels.length);
            chosen.push(validPixels.splice(i, 1)[0]);
          }}

          chosen.forEach(p => {{
            const r = data[p.index];
            const g = data[p.index + 1];
            const b = data[p.index + 2];
            const startX = Math.random() * canvas.width;
            const startY = Math.random() * canvas.height;
            particles.push({{
              x: startX,
              y: startY,
              targetX: p.x + (canvas.width / 2 - iw / 2),
              targetY: p.y + (canvas.height / 2 - ih / 2),
              color: `rgba(${{r}}, ${{g}}, ${{b}}, 1)`,
              alpha: 0,
              vx: 0,
              vy: 0
            }});
          }});

          animate();
        }};

        function animate(timestamp) {{
          if (!startTime) startTime = timestamp;
          const elapsed = (timestamp - startTime) / 1000; // seconds
          const duration = 3.5; // logo formation duration

          ctx.clearRect(0, 0, canvas.width, canvas.height);
          let allClose = true;

          particles.forEach(p => {{
            let dx = p.targetX - p.x;
            let dy = p.targetY - p.y;

            if (elapsed < duration) {{
                // initial slow convergence
                const factor = 0.02;
                p.vx = dx * factor;
                p.vy = dy * factor;
                p.x += p.vx;
                p.y += p.vy;
                allClose = false;
            }} else {{
                // gentle floating
                const floatRange = 0.5;
                p.x += (Math.random() - 0.5) * floatRange;
                p.y += (Math.random() - 0.5) * floatRange;

                // mouse repulsion only if cursor over canvas
                if (mouse.x !== null && mouse.y !== null) {{
                    const mx = p.x - mouse.x;
                    const my = p.y - mouse.y;
                    const mdist = Math.sqrt(mx*mx + my*my);
                    if (mdist < 80) {{
                        const push = 8 * (1 - mdist / 80);
                        p.x += (mx/mdist) * push + (Math.random() - 0.5) * 2;
                        p.y += (my/mdist) * push + (Math.random() - 0.5) * 2;
                    }}
                }}

                // smoothly return to target
                const returnFactor = 0.02;
                p.x += (p.targetX - p.x) * returnFactor;
                p.y += (p.targetY - p.y) * returnFactor;
            }}

            // fade in
            if (p.alpha < 1) p.alpha += 0.03;

            // draw glowing particle
            ctx.beginPath();
            ctx.arc(p.x, p.y, radius, 0, Math.PI*2);
            ctx.fillStyle = p.color.replace('1)', `${{p.alpha}})`);
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 12;
            ctx.fill();
          }});

          if (!formed && allClose) formed = true;
          requestAnimationFrame(animate);
        }}
      </script>
    </body>
    </html>
    """

    components.html(html_code, height=400, width=700)
