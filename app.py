import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
from pydantic import BaseModel
import json

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(page_title="NutriScan AI", page_icon="🌿", layout="centered")

st.markdown("""
<style>
    /* Soft, organic off-white background */
    .stApp {
        background-color: #F7FCF8;
    }
    
    /* Deep Forest Green Typography */
    .main-title {
        text-align: center;
        color: #0A3A2A;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: -10px;
    }
    .sub-title {
        text-align: center;
        color: #4A7A59;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
        font-weight: 500;
    }
    
    /* Clean White Nutrition Cards */
    .nutrition-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        border: 1px solid #E8F5E9;
        margin-bottom: 15px;
    }
    
    /* Hide Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. THE BLUEPRINT ---
class BadIngredient(BaseModel):
    name: str
    explanation: str

class FoodAnalysis(BaseModel):
    product_identified: str
    health_rating: int
    verdict: str
    bad_ingredients: list[BadIngredient]
    good_ingredients: list[str]
    healthy_replacements: list[str]

# --- 3. THE FRONTEND UI ---
st.markdown("<h1 class='main-title'>🌿 NutriScan AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Clinical-grade ingredient analysis at your fingertips.</p>", unsafe_allow_html=True)

# Load the secure API key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🔒 App is locked. Please add your API Key to Streamlit Secrets.")
    st.stop()

# --- INPUT TABS ---
st.markdown("<div class='nutrition-card'>", unsafe_allow_html=True)
tab_upload, tab_camera = st.tabs(["📁 Upload Image", "📸 Scan Label"])

with tab_upload:
    uploaded_file = st.file_uploader("Select an ingredient list (JPG, PNG)", type=["jpg", "jpeg", "png"], label_visibility="hidden")

with tab_camera:
    camera_photo = st.camera_input("Take a clear picture of the ingredients")
st.markdown("</div>", unsafe_allow_html=True)

image_to_process = uploaded_file if uploaded_file is not None else camera_photo

# --- 4. THE LOGIC & DISPLAY ---
if image_to_process is not None:
    client = genai.Client(api_key=api_key)
    img = PIL.Image.open(image_to_process)
    
    prompt = """
    You are an expert clinical nutritionist. Analyze the ingredients in this image.
    Fill out the required data structure accurately.
    For bad ingredients, explain the complex chemical names in simple terms.
    Suggest 2-3 healthier, whole-food alternatives.
    """
    
    with st.status("🔬 Analyzing nutritional profile and chemical composition...", expanded=True) as status:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, img],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FoodAnalysis,
                ),
            )
            data = json.loads(response.text)
            status.update(label="Analysis Complete", state="complete", expanded=False)
            
            # --- THE DASHBOARD LAYOUT ---
            st.divider() 
            
            # Wrap the top results in a clean white card
            st.markdown("<div class='nutrition-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.image(img, use_container_width=True, border_radius=8)
                
            with col2:
                st.markdown(f"<h3 style='color:#0A3A2A; margin-top:0;'>{data['product_identified']}</h3>", unsafe_allow_html=True)
                
                if data['health_rating'] >= 7:
                    st.success(f"**Verdict:** {data['verdict']} \n\n**Health Score:** {data['health_rating']}/10")
                elif data['health_rating'] >= 4:
                    st.warning(f"**Verdict:** {data['verdict']} \n\n**Health Score:** {data['health_rating']}/10")
                else:
                    st.error(f"**Verdict:** {data['verdict']} \n\n**Health Score:** {data['health_rating']}/10")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("") 
            
            # Data breakdown tabs
            tab1, tab2, tab3 = st.tabs(["⚠️ Additive Warnings", "✅ Natural Ingredients", "🥗 Clean Alternatives"])
            
            with tab1:
                st.markdown("<div class='nutrition-card'>", unsafe_allow_html=True)
                if len(data['bad_ingredients']) == 0:
                    st.write("🌿 **Clean Label:** No major artificial additives or red flags found.")
                else:
                    for item in data['bad_ingredients']:
                        st.markdown(f"**<span style='color:#D32F2F;'>{item['name']}</span>**", unsafe_allow_html=True)
                        st.write(f"{item['explanation']}")
                        st.divider()
                st.markdown("</div>", unsafe_allow_html=True)
                        
            with tab2:
                st.markdown("<div class='nutrition-card'>", unsafe_allow_html=True)
                for item in data['good_ingredients']:
                    st.write(f"🌿 {item}")
                st.markdown("</div>", unsafe_allow_html=True)
                    
            with tab3:
                st.markdown("<div class='nutrition-card'>", unsafe_allow_html=True)
                st.write("**Dietitian recommended alternatives:**")
                for item in data['healthy_replacements']:
                    st.write(f"🥑 {item}")
                st.markdown("</div>", unsafe_allow_html=True)
                    
        except Exception as e:
            status.update(label="Analysis Failed", state="error", expanded=False)
            st.error(f"Something went wrong: {e}")
