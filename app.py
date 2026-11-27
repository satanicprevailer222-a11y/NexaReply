
import streamlit as st
import openai
from anthropic import Anthropic
from google import genai
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(
    page_title="NexaReply | AI Response Comparison",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
.main-title {
    font-size: 2.4rem !important;
    font-weight: 700;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: #888;
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
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="main-title">🤖 NexaReply</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="subtitle">Compare ChatGPT, Claude & Gemini side-by-side</p>',
    unsafe_allow_html=True
)

# API keys
with st.sidebar:
    st.header("🔑 Your API Keys")
    st.caption("Keys are used to call the respective AI providers. They are not saved by this app.")

    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-..."
    )

    anthropic_key = st.text_input(
        "Anthropic (Claude) API Key",
        type="password",
        placeholder="sk-ant-..."
    )

    gemini_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza..."
    )

    st.markdown("---")
    st.markdown("**Get your API keys:**")
    st.markdown("- [Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.markdown("- [OpenAI](https://platform.openai.com/api-keys)")
    st.markdown("- [Anthropic](https://console.anthropic.com/)")

    st.info("You can start with only your Gemini API key.")

# Prompt input
prompt = st.text_area(
    "Enter your prompt / question",
    height=120,
    placeholder="Example: Write a professional business email..."
)

# AI response functions
def get_openai_response(prompt, api_key):
    if not api_key:
        return "⚠️ OpenAI API key not provided."

    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content or "No response generated."

    except Exception as e:
        return f"❌ OpenAI Error: {str(e)}"


def get_claude_response(prompt, api_key):
    if not api_key:
        return "⚠️ Claude API key not provided."

    try:
        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return "\n".join(
            block.text for block in response.content
            if block.type == "text"
        ) or "No text response generated."

    except Exception as e:
        return f"❌ Claude Error: {str(e)}"


def get_gemini_response(prompt, api_key):
    if not api_key:
        return "⚠️ Gemini API key not provided."

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return response.text or "Gemini returned an empty response."

    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"


# Generate responses
if st.button("🚀 Generate Replies from All Models", use_container_width=True):

    if not prompt.strip():
        st.warning("Please enter a question first.")

    elif not any([openai_key, anthropic_key, gemini_key]):
        st.warning("Please enter at least one API key.")

    else:
        with st.spinner("Generating AI responses... Please wait."):

            with ThreadPoolExecutor(max_workers=3) as executor:

                future_openai = executor.submit(
                    get_openai_response, prompt, openai_key
                )

                future_claude = executor.submit(
                    get_claude_response, prompt, anthropic_key
                )

                future_gemini = executor.submit(
                    get_gemini_response, prompt, gemini_key
                )

                openai_reply = future_openai.result()
                claude_reply = future_claude.result()
                gemini_reply = future_gemini.result()

        st.markdown("## Results")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("### 🟢 ChatGPT")
            with st.container(border=True):
                st.markdown(openai_reply)

        with col_b:
            st.markdown("### 🟣 Claude")
            with st.container(border=True):
                st.markdown(claude_reply)

        with col_c:
            st.markdown("### 🔵 Gemini")
            with st.container(border=True):
                st.markdown(gemini_reply)

        st.success("Response generation completed.")


# Footer
st.markdown("---")
st.caption("NexaReply | AI-Powered Response Comparison")
