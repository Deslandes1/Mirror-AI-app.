import streamlit as st
import cv2
import numpy as np
import asyncio
import tempfile
import base64
import os
import subprocess

# Page config
st.set_page_config(page_title="Mirror AI – Your Talking Reflection", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    h1, h2, h3 { color: #48dbfb; }
    .stButton button { background-color: #ff6b35; color: white; border-radius: 30px; font-weight: bold; }
    .stAlert { background-color: #1e2130; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🪞 Mirror AI – Your Talking Reflection")
st.markdown("Look into the camera, type your question, and your reflection will answer with voice.")

# Sidebar for API key and settings
with st.sidebar:
    st.image("https://flagcdn.com/w320/ht.png", width=80)
    st.markdown("### GlobalInternet.py")
    st.markdown("**Founder:** Gesner Deslandes")
    st.markdown("📞 WhatsApp: (509) 4738-5663")
    st.markdown("📧 deslandes78@gmail.com")
    st.markdown("---")
    
    # LLM provider selection
    llm_provider = st.selectbox("Choose LLM Provider", ["OpenAI", "Groq", "Gemini"])
    
    api_key = ""
    if llm_provider == "OpenAI":
        api_key = st.text_input("OpenAI API Key", type="password", help="Get from platform.openai.com/api-keys")
        model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4o-mini"])
    elif llm_provider == "Groq":
        api_key = st.text_input("Groq API Key", type="password", help="Get from console.groq.com")
        model = st.selectbox("Model", ["llama3-70b-8192", "mixtral-8x7b-32768"])
    else:  # Gemini
        api_key = st.text_input("Gemini API Key", type="password", help="Get from makersuite.google.com/app/apikey")
        model = "gemini-1.5-flash"
    
    st.markdown("---")
    st.markdown("### 💰 Price")
    st.markdown("**$149 USD** (full source code, lifetime updates)")
    st.markdown("---")
    st.markdown("© 2025 GlobalInternet.py")

# Initialize session state
if "mirror_response" not in st.session_state:
    st.session_state.mirror_response = ""

# Webcam feed
st.markdown("### 🎥 Your Reflection")
frame_placeholder = st.empty()
camera_running = st.checkbox("Start Camera", value=True)

# Audio output function (using edge-tts subprocess – reliable)
def speak(text):
    """Convert text to speech and play it."""
    if not text.strip():
        return
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        cmd = ["edge-tts", "--voice", "en-US-GuyNeural", "--text", text, "--write-media", tmp.name]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
            with open(tmp.name, "rb") as f:
                audio_bytes = f.read()
                b64 = base64.b64encode(audio_bytes).decode()
                st.markdown(f'<audio controls autoplay src="data:audio/mp3;base64,{b64}" style="width: 100%;"></audio>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Audio error: {e}")
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

# LLM answer generation
def get_llm_answer(question, provider, key, model_name):
    if not key:
        st.error(f"Please enter your {provider} API key.")
        return None
    try:
        if provider == "OpenAI":
            from openai import OpenAI
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful, friendly AI that speaks as if you are the person's reflection in the mirror. Answer concisely and naturally."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        elif provider == "Groq":
            from groq import Groq
            client = Groq(api_key=key)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful, friendly AI that speaks as if you are the person's reflection in the mirror. Answer concisely and naturally."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        elif provider == "Gemini":
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(f"You are a helpful, friendly AI that speaks as if you are the person's reflection in the mirror. Answer concisely and naturally.\n\nUser: {question}")
            return response.text
    except Exception as e:
        st.error(f"LLM error: {e}")
        return None

# Camera feed
if camera_running:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Cannot access camera. Please check permissions.")
    else:
        while camera_running:
            ret, frame = cap.read()
            if ret:
                # Flip horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            else:
                break
        cap.release()

# Question input (text only)
st.markdown("---")
st.markdown("### 💬 Ask the Mirror")

text_question = st.text_input("Type your question here:", placeholder="e.g., What is the meaning of life?")
if st.button("Ask the Mirror", use_container_width=True) and text_question:
    with st.spinner("Mirror is thinking..."):
        answer = get_llm_answer(text_question, llm_provider, api_key, model)
        if answer:
            st.session_state.mirror_response = answer
            st.success(f"🪞 Mirror says: {answer}")
            speak(answer)

if st.session_state.mirror_response:
    st.markdown("---")
    st.markdown(f"**Last mirror response:** {st.session_state.mirror_response}")

st.markdown("---")
st.caption("🪞 Look at yourself, type a question, and your reflection will answer with voice. Powered by AI and edge-tts.")
