import streamlit as st
from PIL import Image, ImageEnhance
from rembg import remove
import replicate
import io

st.set_page_config(page_title="AI Thumbnail Creator", layout="wide")
st.title("🔥 AI Fantasy Thumbnail Creator")

# Replicate API Key ထည့်ရန်
api_key = st.sidebar.text_input("Replicate API Key ထည့်ပါ", type="password")

col1, col2 = st.columns(2)

with col1:
    st.subheader("၁။ မိမိပုံ နှင့် နောက်ခံပုံ တင်ပါ")
    user_file = st.file_uploader("မိမိ ဇာတ်ကောင်ပုံ/ဓာတ်ပုံ တင်ပါ", type=["png", "jpg", "jpeg"])
    bg_file = st.file_uploader("နောက်ခံ Fantasy ပုံ တင်ပါ (မရှိလျှင် AI နှင့် ထုတ်ပါ)", type=["png", "jpg", "jpeg"])
    
    prompt = st.text_area("AI Background/Effect Prompt (Optional)", 
                          "3D Donghua style, Chinese Xianxia animation background, glowing blue energy dragon, fiery aura, 8k render")

with col2:
    st.subheader("၂။ ပုံစမ်းသပ်မှု ပရီဗျူး (Preview)")
    
    if user_file:
        # နောက်ခံဖျက်ခြင်း (Remove Background)
        input_img = Image.open(user_file)
        st.text("ဇာတ်ကောင်ပုံမှ နောက်ခံကို ဖျက်နေပါသည်...")
        subject_img = remove(input_img)
        
        # AI Background ထုတ်လုပ်ခြင်း (Replicate သုံးထားပါက)
        if st.button("Thumbnail စတင်ဖန်တီးမည်"):
            if bg_file:
                background = Image.open(bg_file).resize((1280, 720))
            elif api_key:
                st.text("AI ထံမှ နောက်ခံပုံ တောင်းယူနေပါသည်...")
                import os
                os.environ["REPLICATE_API_TOKEN"] = api_key
                
                # Flux သို့မဟုတ် SDXL မော်ဒယ်ဖြင့် AI နောက်ခံထုတ်ခြင်း
                output = replicate.run(
                    "black-forest-labs/flux-schnell",
                    input={"prompt": prompt, "aspect_ratio": "16:9"}
                )
                
                import requests
                bg_data = requests.get(output[0]).content
                background = Image.open(io.BytesIO(bg_data)).resize((1280, 720))
            else:
                st.error("ကျေးဇူးပြု၍ နောက်ခံပုံ တင်ပါ သို့မဟုတ် Replicate API Key ထည့်ပါ။")
                st.stop()

            # ပုံနှစ်ပုံကို ပေါင်းစပ်ခြင်း (Composite)
            # Subject ပုံကို 16:9 ထဲ ဝင်အောင် အရွယ်အစား ညှိခြင်း
            subject_resized = subject_img.resize((int(background.height * subject_img.width / subject_img.height), background.height))
            
            # Canvas ပေါ်တွင် ပုံနှစ်ပုံ အလွှာထပ်ခြင်း (Layering)
            final_img = background.copy()
            # အလယ်တည့်တည့် သို့မဟုတ် ဘေးတွင် ထားခြင်း
            position = ((final_img.width - subject_resized.width) // 2, 0)
            final_img.paste(subject_resized, position, mask=subject_resized)
            
            st.image(final_img, caption="ဖန်တီးပြီးသော Thumbnail", use_column_width=True)
            
            # Download Button
            buf = io.BytesIO()
            final_img.save(buf, format="PNG")
            st.download_button("Thumbnail ဒေါင်းလုဒ်ဆွဲရန်", data=buf.getvalue(), file_name="thumbnail.png", mime="image/png")
