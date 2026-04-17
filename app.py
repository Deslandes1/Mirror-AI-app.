import streamlit as st
import asyncio
import tempfile
import base64
import os
import subprocess

st.set_page_config(page_title="Mirror AI – Your Talking Reflection", layout="wide")

# Custom CSS – mirror effect (flip horizontally) + all text white
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white !important;
    }
    /* Mirror effect: flip the camera image horizontally */
    .stCameraInput video {
        transform: scaleX(-1);
    }
    /* All text white */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp label, .stApp .stMarkdown, .stApp .stText, .stApp .stCaption, .stApp .stInfo,
    .stApp .stSuccess, .stApp .stWarning, .stApp .stError, .stApp .stRadio label,
    .stApp .stSelectbox label, .stApp .stSlider label, .stApp .stFileUploader label,
    .stApp .stTextArea label, .stApp .stButton button, .stApp .stAlert, .stApp .stException,
    .stApp .stCodeBlock, .stApp .stDataFrame, .stApp .stTable, .stApp .stTabs [role="tab"],
    .stApp .stTabs [role="tablist"] button, .stApp .stExpander, .stApp .stProgress > div,
    .stApp .stMetric label, .stApp .stMetric value, div, p, span, pre, code,
    .element-container, .stText p, .stText div, .stText span, .stText code {
        color: white !important;
    }
    /* Dropdown options black */
    div[data-baseweb="popover"] ul {
        background-color: #f0f2f6 !important;
        border: 1px solid #cccccc;
    }
    div[data-baseweb="popover"] li {
        color: black !important;
        background-color: #f0f2f6 !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #d0d4dc !important;
    }
    /* Password input black text */
    input[type="password"] {
        color: black !important;
        background-color: #ffffff !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #2d1b4e;
        border: 1px solid #ffcc00;
        border-radius: 10px;
    }
    .stSelectbox div[data-baseweb="select"] div {
        color: white !important;
    }
    .stButton button {
        background-color: #ff6b35 !important;
        color: white !important;
        border-radius: 30px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #feca57 !important;
        color: black !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1a0b2e, #2d1b4e);
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stText,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }
    .stAlert {
        background-color: rgba(0,0,0,0.6) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🪞 Mirror AI – Your Talking Reflection")
st.markdown("Look into the camera, type your question, and your reflection will answer with voice.")

with st.sidebar:
    st.image("https://flagcdn.com/w320/ht.png", width=80)
    st.markdown("### GlobalInternet.py")
    st.markdown("**Founder:** Gesner Deslandes")
    st.markdown("📞 WhatsApp: (509) 4738-5663")
    st.markdown("📧 deslandes78@gmail.com")
    st.markdown("---")
    
    llm_provider = st.selectbox("Choose LLM Provider", ["OpenAI", "Groq", "Gemini"])
    api_key = ""
    if llm_provider == "OpenAI":
        api_key = st.text_input("OpenAI API Key", type="password")
        model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4o-mini"])
    elif llm_provider == "Groq":
        api_key = st.text_input("Groq API Key", type="password")
        model = st.selectbox("Model", ["llama3-70b-8192", "mixtral-8x7b-32768"])
    else:
        api_key = st.text_input("Gemini API Key", type="password")
        model = "gemini-1.5-flash"
    
    st.markdown("---")
    st.markdown("### 💰 Price")
    st.markdown("**$149 USD** (full source code, lifetime updates)")
    st.markdown("---")
    st.markdown("© 2025 GlobalInternet.py")

if "mirror_response" not in st.session_state:
    st.session_state.mirror_response = ""

# Mirror camera – using st.camera_input (works in cloud)
st.markdown("### 🎥 Your Reflection")
camera_photo = st.camera_input("", label_visibility="collapsed")
# The camera input automatically shows the live feed; no need to capture a photo.
# We just display the mirrored feed via CSS.

# Audio function (unchanged)
def speak(text):
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

st.markdown("---")
st.markdown("### 💬 Ask the Mirror")
text_question = st.text_input("Type your question here:")
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
st.caption("🪞 Look at yourself, type a question, and your reflection will answer with voice.")
