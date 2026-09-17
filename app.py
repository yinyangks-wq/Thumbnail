import streamlit as st
from PIL import Image, ImageFilter
import replicate
import requests
import io
import os

st.set_page_config(page_title="AI Thumbnail Creator", layout="wide")
st.title("🔥 AI Fantasy Thumbnail Creator")

# Sidebar Controls
st.sidebar.header("⚙️ ဇာတ်ကောင် ပုံစံ ချိန်ညှိရန်")
scale = st.sidebar.slider("ဇာတ်ကောင် အရွယ်အစား (Scale)", 0.2, 1.2, 0.65, 0.05)
pos_x = st.sidebar.slider("ဘယ်/ညာ နေရာ (X Position)", 0.0, 1.0, 0.5, 0.02)
pos_y = st.sidebar.slider("အပေါ်/အောက် နေရာ (Y Position)", 0.0, 1.0, 0.5, 0.02)

api_key = st.sidebar.text_input("Replicate API Key ထည့်ပါ", type="password")

col1, col2 = st.columns(2)

with col1:
    st.subheader("၁။ ပုံနှင့် နောက်ခံ တင်ပါ")
    user_file = st.file_uploader("ဇာတ်ကောင်ပုံ တင်ပါ (Background ဖျက်ပြီးသား PNG ဖြစ်ရပါမည်)", type=["png"])
    bg_file = st.file_uploader("နောက်ခံ Fantasy ပုံ တင်ပါ", type=["png", "jpg", "jpeg"])
    
    prompt = st.text_area("AI Background Prompt", 
                          "3D Donghua style, Chinese Xianxia animation background, glowing blue energy dragon, fiery aura, 8k render")

with col2:
    st.subheader("၂။ သေသေသပ်သပ် ပရီဗျူး")
    
    if st.button("Thumbnail စတင်ဖန်တီးမည်"):
        background = None
        
        # 1. Background ပြင်ဆင်ခြင်း
        if bg_file:
            background = Image.open(bg_file).convert("RGBA").resize((1280, 720))
        elif api_key:
            try:
                st.info("AI ထံမှ နောက်ခံပုံ တောင်းယူနေပါသည်...")
                os.environ["REPLICATE_API_TOKEN"] = api_key
                
                output = replicate.run(
                    "black-forest-labs/flux-schnell",
                    input={"prompt": prompt, "aspect_ratio": "16:9"}
                )
                
                bg_data = requests.get(output[0]).content
                background = Image.open(io.BytesIO(bg_data)).convert("RGBA").resize((1280, 720))
            except Exception as e:
                st.error(f"AI ပုံထုတ်ရာတွင် အမှားအယွင်းရှိပါသည်: {e}")
        else:
            st.warning("ကျေးဇူးပြု၍ နောက်ခံပုံ တင်ပါ သို့မဟုတ် Replicate API Key ထည့်ပါ။")

        # 2. ဇာတ်ကောင်နှင့် နောက်ခံ သေသေသပ်သပ် ပေါင်းစပ်ခြင်း
        if background and user_file:
            subject_img = Image.open(user_file).convert("RGBA")
            
            # Slider အတိုင်း အရွယ်အစား ညှိခြင်း
            new_height = int(background.height * scale)
            aspect_ratio = subject_img.width / subject_img.height
            new_width = int(new_height * aspect_ratio)
            subject_resized = subject_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Slider အတိုင်း နေရာချခြင်း
            x_offset = int((background.width - new_width) * pos_x)
            y_offset = int((background.height - new_height) * pos_y)
            
            # Layer အလွှာထပ်ခြင်း
            final_img = background.copy()
            final_img.paste(subject_resized, (x_offset, y_offset), mask=subject_resized)
            
            st.image(final_img, caption="သေသေသပ်သပ် ဖန်တီးထားသော Thumbnail", use_container_width=True)
            
            buf = io.BytesIO()
            final_img.save(buf, format="PNG")
            st.download_button("Thumbnail ဒေါင်းလုဒ်ဆွဲရန်", data=buf.getvalue(), file_name="thumbnail.png", mime="image/png")
