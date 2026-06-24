import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Image to Prompt Builder", layout="wide")
st.title("📸 Image-to-Prompt Converter & Builder")
st.write("Upload foto model/karakter, biarkan AI menganalisis, lalu modifikasi detailnya sesuka lu!")

# Input API Key dari sidebar
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    st.info("Dapatkan API Key gratis di Google AI Studio.")

# Inisialisasi State agar data tidak hilang saat dropdown diubah
if "analyzed_data" not in st.session_state:
    st.session_state.analyzed_data = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# Layouting: Kiri untuk Input & Preview, Kanan untuk Controls & Output
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Upload Gambar")
    uploaded_file = st.file_uploader("Pilih gambar karakter...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar yang di-upload", use_container_width=True)
        
        # Reset state jika user upload gambar baru yang berbeda
        if st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.analyzed_data = None
            st.session_state.last_uploaded_file = uploaded_file.name

        # Tombol Analisis
        if st.button("🚀 Analisis Karakter & Detail", type="primary"):
            if not api_key:
                st.error("Masukkan API Key dulu di sidebar sebelah kiri!")
            else:
                with st.spinner("AI sedang membaca detail gambar..."):
                    try:
                        # Inisialisasi Client Gemini SDK terbaru (v0.1+)
                        client = genai.Client(api_key=api_key)
                        
                        # Prompt untuk memaksa Gemini mengembalikan format JSON yang rapi
                        prompt_analysis = """
                        Analyze this image of a character/person. Extract the details and return them strictly in JSON format with the following keys. 
                        Keep the values concise, in English (standard for image generators like Midjourney/Stable Diffusion):
                        {
                            "gender": "e.g., male, female, or non-binary",
                            "expression": "e.g., smiling, neutral, angry",
                            "pose": "e.g., standing arms crossed, sitting, looking over shoulder",
                            "shot_type": "e.g., close-up shot, medium shot, full-body shot",
                            "camera_angle": "e.g., eye-level, low angle, high angle",
                            "background": "e.g., cyberpunk city street neon light, clean studio backdrop, nature forest",
                            "art_style": "e.g., photorealistic, 3D Pixar style, anime illustration, oil painting",
                            "lighting": "e.g., cinematic lighting, dramatic rim light, soft studio lighting"
                        }
                        Do not include any markdown formatting like ```json or text outside the JSON object.
                        """
                        
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=[image, prompt_analysis],
                        )
                        
                        # Parse hasil ke JSON
                        st.session_state.analyzed_data = json.loads(response.text.strip())
                        st.success("Analisis selesai! Silakan cek opsi di sebelah kanan.")
                    except Exception as e:
                        st.error(f"Gagal menganalisis gambar: {e}")

with col2:
    st.subheader("2. Modifikasi Detail (Dropdown)")
    
    # Ambil data dari AI jika sudah dianalisis, jika belum pakai string kosong
    data = st.session_state.analyzed_data if st.session_state.analyzed_data else {}
    
    # Fungsi pembantu untuk memastikan opsi bawaan AI masuk ke dalam list pilihan dropdown
    def get_options(key, default_list):
        ai_value = data.get(key, "")
        if ai_value and ai_value not in default_list:
            return [ai_value] + default_list
        return default_list

    # Define list opsi manual sebagai variasi tambahan
    genders = ["male", "female", "android", "cyborg"]
    expressions = ["neutral", "smiling warmly", "smirking", "intense stare", "crying", "determined"]
    poses = ["standing straight", "sitting on a chair", "dynamic action pose", "arms crossed", "looking back"]
    shots = ["close-up shot", "medium shot (MCU)", "full-body shot", "extreme close-up"]
    angles = ["eye-level angle", "low angle (hero shot)", "high angle", "bird's-eye view"]
    backgrounds = ["clean studio background", "cyberpunk neon city at night", "ancient fantasy ruins", "minimalist cafe", "abstract gradient"]
    styles = ["photorealistic, 8k resolution", "3D render, Unreal Engine 5 style", "anime key visual", "dark fantasy concept art", "oil painting"]
    lightings = ["soft studio lighting", "cinematic dramatic lighting", "neon rim lighting", "golden hour natural light", "volumetric fog lighting"]

    # Buat UI Dropdown (Jika AI sudah deteksi, dia otomatis milih hasil deteksi AI sebagai default)
    selected_gender = st.selectbox("Gender", get_options("gender", genders))
    selected_expression = st.selectbox("Ekspresi", get_options("expression", expressions))
    selected_pose = st.selectbox("Pose", get_options("pose", poses))
    selected_shot = st.selectbox("Shot Type", get_options("shot_type", shots))
    selected_angle = st.selectbox("Camera Angle", get_options("camera_angle", angles))
    selected_bg = st.selectbox("Background / Lokasi", get_options("background", backgrounds))
    selected_style = st.selectbox("Art Style", get_options("art_style", styles))
    selected_lighting = st.selectbox("Lighting", get_options("lighting", lightings))
    
    # Input tambahan manual biar makin detail
    extra_detail = st.text_input("Detail Tambahan Tambahan (Contoh: wearing tactical jacket, silver hair, dll)", "")

    st.write("---")
    st.subheader("3. Hasil Prompt Akhir")
    
    # Rangkai seluruh input menjadi satu prompt terstruktur
    prompt_elements = [
        f"A detailed {selected_style} of a {selected_gender}",
        f"with a {selected_expression} expression",
        f"{selected_pose}",
        f"{selected_shot}",
        f"shot from a {selected_angle}",
        f"located in a {selected_bg}",
        f"illuminated by {selected_lighting}"
    ]
    
    if extra_detail:
        prompt_elements.append(extra_detail)
        
    final_prompt = ", ".join(prompt_elements) + " --ar 16:9 --v 6.0" # Default parameter Midjourney contohnya
    
    # Tampilkan prompt akhir di text area agar mudah di-copy
    st.text_area("Copy prompt di bawah ini ke Midjourney / Stable Diffusion / DALL-E:", final_prompt, height=120)