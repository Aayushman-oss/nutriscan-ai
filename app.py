import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
from pydantic import BaseModel
import json
import urllib.parse

# --- 1. PREMIUM PAGE CONFIG & GLASSMORPHISM CSS ---
st.set_page_config(page_title="NutriScan AI", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    /* Charcoal Dark Mode Background */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    
    /* Typography & Core Message */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: -webkit-linear-gradient(#00FFCC, #0088FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
        color: #A0A0A0;
        letter-spacing: 2px;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Neon Accents & Minimalist tweaks */
    hr { border-color: rgba(0, 255, 204, 0.2); }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #888; border-radius: 4px; }
    .stTabs [aria-selected="true"] { color: #00FFCC !important; border-bottom: 2px solid #00FFCC !important; }
    
    /* Hide Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. THE NEW BLUEPRINTS (PYDANTIC) ---
class Additive(BaseModel):
    name: str
    e_number: str
    explanation: str
    risk_level: str # "Red", "Yellow", or "Green"

class ScanResult(BaseModel):
    product_identified: str
    psychological_insights: list[str]
    calories_estimate: str
    sugar_levels: str
    sodium_levels: str
    preservatives_found: list[str]
    additives: list[Additive]

class Alternative(BaseModel):
    name: str
    reason: str
    image_search_prompt: str # Used to fetch an image

class AltSearch(BaseModel):
    alternatives: list[Alternative]

# --- 3. FRONTEND HEADER ---
st.markdown("<div class='hero-title'>Decode What You Eat.</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>SCAN. ANALYZE. UNDERSTAND.</div>", unsafe_allow_html=True)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("🔒 App locked. Add API Key to Streamlit Secrets.")
    st.stop()

# --- MAIN NAVIGATION TABS ---
nav_scan, nav_search = st.tabs(["⚡ AI Scanner", "🔍 Find Alternatives"])

# ==========================================
# TAB 1: THE SCANNER
# ==========================================
with nav_scan:
    st.markdown("<div class='glass-card' style='text-align: center; border-color: #00FFCC;'>", unsafe_allow_html=True)
    scan_method = st.radio("Input Method:", ["📸 Camera", "📁 Upload"], horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    image_to_process = None
    if scan_method == "📸 Camera":
        image_to_process = st.camera_input("Scanner Active", label_visibility="hidden")
    else:
        image_to_process = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="hidden")

    if image_to_process is not None:
        img = PIL.Image.open(image_to_process)
        
        prompt = """
        Analyze this food label/ingredients. If nutrition facts aren't visible, estimate based on ingredients.
        Provide 2 'psychological insights' (e.g., 'Equivalent to 5 teaspoons of sugar' or 'Contains 3 high-risk additives').
        Extract calories, sugar, and sodium levels. List preservatives. 
        List additives with their E-numbers and rank risk as 'Red', 'Yellow', or 'Green'.
        """
        
        with st.status("Scanning molecular profile...", expanded=True) as status:
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt, img],
                    config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=ScanResult),
                )
                data = json.loads(response.text)
                status.update(label="Analysis Complete.", state="complete", expanded=False)
                
                # --- RESULTS UI ---
                st.markdown(f"<h3 style='color:#00FFCC; text-align:center;'>{data['product_identified'].upper()}</h3>", unsafe_allow_html=True)
                
                # Psychological Insights (The "Smart Highlight")
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0px;'>🧠 AI Insights</h4>", unsafe_allow_html=True)
                for insight in data['psychological_insights']:
                    st.markdown(f"<li>{insight}</li>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Core Macros
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"<div class='glass-card'><b>Calories</b><br>{data['calories_estimate']}</div>", unsafe_allow_html=True)
                col2.markdown(f"<div class='glass-card'><b>Sugar</b><br>{data['sugar_levels']}</div>", unsafe_allow_html=True)
                col3.markdown(f"<div class='glass-card'><b>Sodium</b><br>{data['sodium_levels']}</div>", unsafe_allow_html=True)
                
                # Additives & E-Numbers
                st.markdown("<h4>🧪 Additive Breakdown</h4>", unsafe_allow_html=True)
                for add in data['additives']:
                    color = "#FF4B4B" if add['risk_level'] == "Red" else "#FFD166" if add['risk_level'] == "Yellow" else "#06D6A0"
                    st.markdown(f"""
                    <div class='glass-card' style='border-left: 5px solid {color};'>
                        <b style='color:{color};'>{add['name']} ({add['e_number']})</b><br>
                        <span style='font-size: 0.9em; color:#CCC;'>{add['explanation']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                status.update(label="Scan Failed", state="error")
                st.error(e)

# ==========================================
# TAB 2: THE ALTERNATIVE SEARCH
# ==========================================
with nav_search:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    search_query = st.text_input("Enter a junk food (e.g., Maggi, Doritos, Coke) to find clean alternatives:", placeholder="Search bad food...")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if search_query:
        alt_prompt = f"""
        The user is looking for healthy, whole-food alternatives to '{search_query}'.
        Provide 3 specific, healthy alternatives. 
        For each, provide a short 'image_search_prompt' (e.g., 'a bowl of hot whole wheat noodles with vegetables').
        """
        
        with st.spinner("Finding clean alternatives..."):
            try:
                alt_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=alt_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=AltSearch),
                )
                alt_data = json.loads(alt_response.text)
                
                st.markdown(f"### Better choices instead of {search_query}:")
                
                for alt in alt_data['alternatives']:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    colA, colB = st.columns([1, 2])
                    
                    with colA:
                        # Clever trick to generate images dynamically without an API key!
                        encoded_prompt = urllib.parse.quote(alt['image_search_prompt'])
                        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=400&height=400&nologo=true"
                        st.image(image_url, use_container_width=True)
                        
                    with colB:
                        st.markdown(f"<h4 style='color:#00FFCC;'>{alt['name']}</h4>", unsafe_allow_html=True)
                        st.write(alt['reason'])
                        
                    st.markdown("</div>", unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Search failed: {e}")
