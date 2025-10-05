import streamlit as st
def show_header():
    """Display the Mentesa header with styling"""
    st.markdown("<h1 style='text-align:center; font-size:2.2rem; font-weight:700; margin-bottom:0.2em;'>Mentesa V7 kiddi</h1>", unsafe_allow_html=True)
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