# NutriScan AI

NutriScan AI is a multimodal Generative AI application that analyzes food product labels from images and converts complex ingredient information into simple, understandable insights.

The application uses **Google Gemini 2.5 Flash** to identify and analyze ingredients, highlight potentially concerning additives, explain their purpose and possible health considerations, identify beneficial ingredients, and suggest healthier alternatives.

### Key Features

* 📷 Upload a food product or ingredient-label image
* 🤖 AI-powered ingredient analysis using Gemini
* 🧪 Identification of potentially concerning ingredients
* 💡 Plain-language explanations of complex ingredients
* 🥗 Identification of beneficial ingredients
* ⭐ Overall health assessment and verdict
* 🔄 Suggestions for healthier alternatives
* 📊 Structured AI responses using Pydantic models
* 🖥️ Interactive Streamlit interface

### Tech Stack

**Python • Streamlit • Google Gemini 2.5 Flash • Google GenAI SDK • Pydantic • Pillow**

[Live Demo: Play with NutriScan AI Here](https://your-app-link-here.streamlit.app/) 

---

### 🚀 Key Features
* **📸 Smart Scanning:** Snap a live photo or upload an image of any food ingredient label.
* **🧠 Psychological Insights:** Translates standard nutrition facts into impactful, real-world context (e.g., "Equivalent to 5 teaspoons of sugar").
* **🧪 Additive Breakdown:** Extracts complex chemical names and E-numbers, categorizing them by risk level (Red, Yellow, Green).
* **💡 Clean Alternatives:** A built-in search engine that finds healthy, whole-food replacements for popular junk foods and dynamically generates images of the alternatives.
* **📱 Viral Sharing:** Automatically drafts WhatsApp and X (Twitter) messages with the scanned product's score and insights.

---

### 🛠️ Tech Stack
* **Frontend UI:** Streamlit (Python)
* **AI Engine:** Google Gemini 2.5 Flash (via `google-genai` SDK)
* **Data Structuring:** Pydantic (Strict JSON schema enforcement)
* **Image Generation:** Pollinations AI API

---

### 💻 How to Run Locally

If you want to run this machine learning application on your own machine, follow these steps:

**1. Clone the repository**
```bash
git clone [https://your-app-link-here.streamlit.app/](https://your-app-link-here.streamlit.app/)
cd nutriscan-ai
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API Key**
Create a `.streamlit/secrets.toml` file in the root directory and add your Google Gemini API key:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

**4. Launch the app**
```bash
streamlit run app.py
```

---

### ⚠️ Disclaimer
*This application is an AI-powered prototype intended for educational purposes. It does not provide certified medical or dietary advice. Always consult a qualified healthcare or nutrition professional before making major dietary changes.*
