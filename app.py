import streamlit as st
import google.generativeai as genai
import platform

# ==========================================
# IMPORT CUSTOM TOOLS
# ==========================================
# Ensure you have empty __init__.py in the tools folder
from tools import simple_interest
from tools import cleaner
from tools import youtube
from tools import video_maker

# ==========================================
# 1. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Ani-Automation", 
    page_icon="ॐ", 
    layout="wide"
)

# ==========================================
# 2. STYLING
# ==========================================
custom_css = """
<style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #002b36; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button { background-color: #007cc7; color: white; border-radius: 8px; }
    /* Fix for text input visibility in dark mode */
    .stTextInput > div > div > input { color: white; background-color: #262730; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 35px;'>ॐ</h1>", unsafe_allow_html=True) 
    st.caption("Ani-Automation v1.2")
    st.divider()
    menu = st.radio("Navigate", ["🏠 Home", "🛠️ Tools", "🤖 AI Chat", "ℹ️ About"])

# ==========================================
# 4. MAIN CONTENT
# ==========================================

# --- HOME ---
if menu == "🏠 Home":
    st.title("Welcome to Ani-Automation")
    st.markdown("### *Your Modular Automation Hub*")
    st.divider()
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("System is Modular & Scalable.")
        st.write("Navigate to **Tools** to see your scripts in action.")
    with col2:
        st.metric("System OS", platform.system())

# --- TOOLS ---
elif menu == "🛠️ Tools":
    st.title("🛠️ Automation Tools")
    
    # Define Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📺 YouTube", 
        "💰 Interest", 
        "🧹 Cleaner", 
        "🎬 Video Maker"
    ])
    
    with tab1:
        youtube.run_tool()
    with tab2:
        simple_interest.run_tool()
    with tab3:
        cleaner.run_tool()
    with tab4:
        # This calls the function in tools/video_maker.py
        video_maker.run_tool()

# --- AI CHAT ---
elif menu == "🤖 AI Chat":
    st.title("🤖 Ani-Bot")
    
    # Secure API Key Handling
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.sidebar.text_input("Gemini API Key", type="password")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            if "messages" not in st.session_state: 
                st.session_state.messages = []
            
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): 
                    st.markdown(msg["content"])
            
            if prompt := st.chat_input("Ask me..."):
                with st.chat_message("user"): 
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: 
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a Gemini API Key in the sidebar to use the Chatbot.")

# --- ABOUT ---
elif menu == "ℹ️ About":
    st.title("About")
    st.write("Ani-Automation: Modular Python Project.")
    st.success("Successfully deployed with MoviePy v2.0 integration.")