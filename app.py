import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
from pydantic import BaseModel
import json

# --- 1. PAGE CONFIG & CUSTOM CSS (Minimalist Styling) ---
st.set_page_config(page_title="NutriScan AI", page_icon="🍏", layout="centered")

st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2E7D32;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .sub-title {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
st.markdown("<h1 class='main-title'>🍏 NutriScan AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Snap a photo or upload an ingredient label to decode what you are really eating.</p>", unsafe_allow_html=True)

# Load the secure API key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🔒 App is locked. Please add your API Key to Streamlit Secrets.")
    st.stop()

# --- NEW: INPUT TABS (Camera vs Upload) ---
tab_upload, tab_camera = st.tabs(["📁 Upload File", "📸 Take Photo"])

with tab_upload:
    uploaded_file = st.file_uploader("Upload an image (JPG, PNG)", type=["jpg", "jpeg", "png"], label_visibility="hidden")

with tab_camera:
    camera_photo = st.camera_input("Take a picture of the ingredients")

# Determine which image the user provided (if any)
image_to_process = uploaded_file if uploaded_file is not None else camera_photo

# --- 4. THE LOGIC & DISPLAY ---
# Run the AI only if an image is either uploaded OR taken via camera
if image_to_process is not None:
    client = genai.Client(api_key=api_key)
    img = PIL.Image.open(image_to_process)
    
    prompt = """
    You are an expert nutritionist. Analyze the ingredients in this image.
    Fill out the required data structure accurately.
    For bad ingredients, explain the complex chemical names in simple terms.
    Suggest 2-3 healthier, whole-food alternatives.
    """
    
    with st.status("🔍 AI is analyzing the label...", expanded=True) as status:
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
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            # --- THE DASHBOARD LAYOUT ---
            st.divider() 
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.image(img, use_container_width=True)
                
            with col2:
                st.subheader(f"{data['product_identified']}")
                
                if data['health_rating'] >= 7:
                    st.success(f"**Verdict:** {data['verdict']} (Score: {data['health_rating']}/10)")
                elif data['health_rating'] >= 4:
                    st.warning(f"**Verdict:** {data['verdict']} (Score: {data['health_rating']}/10)")
                else:
                    st.error(f"**Verdict:** {data['verdict']} (Score: {data['health_rating']}/10)")
            
            st.write("") 
            
            tab1, tab2, tab3 = st.tabs(["⚠️ Red Flags", "✅ Good Stuff", "💡 Better Choices"])
            
            with tab1:
                if len(data['bad_ingredients']) == 0:
                    st.write("Looks incredibly clean! No major red flags found.")
                else:
                    for item in data['bad_ingredients']:
                        st.write(f"**{item['name']}**")
                        st.caption(f"{item['explanation']}")
                        
            with tab2:
                for item in data['good_ingredients']:
                    st.write(f"- {item}")
                    
            with tab3:
                st.write("**Instead of this, try:**")
                for item in data['healthy_replacements']:
                    st.write(f"🍽️ {item}")
                    
        except Exception as e:
            status.update(label="Analysis Failed", state="error", expanded=False)
            st.error(f"Something went wrong: {e}")
