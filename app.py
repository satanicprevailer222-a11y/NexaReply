import streamlit as st
import openai
from anthropic import Anthropic
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import time

st.set_page_config(
    page_title="MultiAI Reply | Compare GPT + Claude + Gemini",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better look
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F46E5;
        color: white;
        height: 3rem;
        font-size: 1.1rem;
        border-radius: 8px;
    }
    .response-box {
        background-color: #f8fafc;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        min-height: 200px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🤖 MultiAI Reply</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Compare responses from ChatGPT, Claude & Gemini side-by-side</p>', unsafe_allow_html=True)

# Sidebar - API Keys
with st.sidebar:
    st.header("🔑 Your API Keys")
    st.caption("Keys stay only in your browser session. Never stored.")
    
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    anthropic_key = st.text_input("Anthropic (Claude) API Key", type="password", placeholder="sk-ant-...")
    gemini_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIza...")
    
    st.markdown("---")
    st.markdown("**How to get free keys:**")
    st.markdown("- Gemini → [aistudio.google.com](https://aistudio.google.com)")
    st.markdown("- OpenAI → [platform.openai.com](https://platform.openai.com)")
    st.markdown("- Claude → [console.anthropic.com](https://console.anthropic.com)")
    
    st.markdown("---")
    st.info("Start with only Gemini key if you want. It has a good free tier.")

# Main Input
prompt = st.text_area(
    "Enter your prompt / question",
    height=120,
    placeholder="Example: Explain quantum computing in simple terms..."
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_btn = st.button("🚀 Generate Replies from All Models", use_container_width=True)

# Functions to call each model
def get_openai_response(prompt, api_key):
    if not api_key:
        return "⚠️ OpenAI key not provided"
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",          # cheaper & fast. Change to gpt-4o if you want
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_claude_response(prompt, api_key):
    if not api_key:
        return "⚠️ Claude key not provided"
    try:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",   # fast & cheap. Use claude-3-5-sonnet for better quality
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_gemini_response(prompt, api_key):
    if not api_key:
        return "⚠️ Gemini key not provided"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")   # or gemini-1.5-pro
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Generate when button clicked
if generate_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        with st.spinner("Calling all models... Please wait 5–15 seconds"):
            # Call all three in parallel
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_openai = executor.submit(get_openai_response, prompt, openai_key)
                future_claude = executor.submit(get_claude_response, prompt, anthropic_key)
                future_gemini = executor.submit(get_gemini_response, prompt, gemini_key)

                openai_reply = future_openai.result()
                claude_reply = future_claude.result()
                gemini_reply = future_gemini.result()

        # Display results in 3 columns
        st.markdown("### Results")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("#### 🟢 ChatGPT (OpenAI)")
            st.markdown(f'<div class="response-box">{openai_reply}</div>', unsafe_allow_html=True)
            st.code(openai_reply, language=None)  # easy copy

        with col_b:
            st.markdown("#### 🟣 Claude (Anthropic)")
            st.markdown(f'<div class="response-box">{claude_reply}</div>', unsafe_allow_html=True)
            st.code(claude_reply, language=None)

        with col_c:
            st.markdown("#### 🔵 Gemini (Google)")
            st.markdown(f'<div class="response-box">{gemini_reply}</div>', unsafe_allow_html=True)
            st.code(gemini_reply, language=None)

# Footer
st.markdown("---")
st.caption("Built with ❤️ | MultiAI Reply MVP | Keys never leave your browser session")