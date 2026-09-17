import streamlit as st
from PIL import Image
import replicate
import requests
import io
import os

st.set_page_config(page_title="AI Thumbnail Creator", layout="wide")
st.title("🔥 AI Fantasy Thumbnail Creator")

# Replicate API Key ထည့်ရန် Sidebar
api_key = st.sidebar.text_input("Replicate API Key ထည့်ပါ", type="password")

col1, col2 = st.columns(2)

with col1:
    st.subheader("၁။ Thumbnail ပြင်ဆင်ရန်")
    user_file = st.file_uploader("မိမိ ပုံတင်ပါ (PNG format ကို အကြံပြုပါသည်)", type=["png", "jpg", "jpeg"])
    bg_file = st.file_uploader("နောက်ခံ Fantasy ပုံ ရှိလျှင် တင်ပါ", type=["png", "jpg", "jpeg"])
    
    prompt = st.text_area("AI Background Prompt", 
                          "3D Donghua style, Chinese Xianxia animation background, glowing blue energy dragon, fiery aura, 8k render")

with col2:
    st.subheader("၂။ ပရီဗျူး (Preview)")
    
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

        # 2. ပုံနှစ်ပုံ ပေါင်းစပ်ခြင်း
        if background and user_file:
            subject_img = Image.open(user_file).convert("RGBA")
            
            # Subject အရွယ်အစား ညှိခြင်း
            aspect_ratio = subject_img.width / subject_img.height
            new_height = background.height
            new_width = int(new_height * aspect_ratio)
            subject_resized = subject_img.resize((new_width, new_height))
            
            # Layer ပေါင်းစပ်ခြင်း
            final_img = background.copy()
            position = ((final_img.width - subject_resized.width) // 2, 0)
            final_img.paste(subject_resized, position, mask=subject_resized)
            
            st.image(final_img, caption="ဖန်တီးပြီးသော Thumbnail", use_column_width=True)
            
            buf = io.BytesIO()
            final_img.save(buf, format="PNG")
            st.download_button("Thumbnail ဒေါင်းလုဒ်ဆွဲရန်", data=buf.getvalue(), file_name="thumbnail.png", mime="image/png")
