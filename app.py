import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Advance Image to Prompt Builder", layout="wide")
st.title("📸 Advance Image-to-Prompt Converter & Builder")
st.write("Upload referensi karakter, tambahkan referensi wajah jika ada, lalu sesuaikan detail fashion dan tone warna!")

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
    st.subheader("1. File Uploads")
    uploaded_file = st.file_uploader("Gambar Utama (Referensi Pose/Vibes)*", type=["jpg", "jpeg", "png"])
    
    # Fitur Baru: Optional Face/Head Reference
    face_file = st.file_uploader("Gambar Wajah/Kepala (Opsional - Untuk Detail Karakter)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Utama", use_container_width=True)
        
        # Reset state jika user upload gambar baru yang berbeda
        if st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.analyzed_data = None
            st.session_state.last_uploaded_file = uploaded_file.name

        if face_file:
            face_image = Image.open(face_file)
            st.image(face_image, caption="Referensi Detail Wajah (Opsional)", width=200)

        # Tombol Analisis
        if st.button("🚀 Analisis Semua Gambar", type="primary"):
            if not api_key:
                st.error("Masukkan API Key dulu di sidebar sebelah kiri!")
            else:
                with st.spinner("AI sedang menganalisis karakteristik visual..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        # Modifikasi prompt analisis agar membaca kedua gambar jika ada
                        prompt_analysis = """
                        Analyze the uploaded image(s) of a character/person. 
                        If a second image focusing on the face is provided, prioritize it for facial features, hair, and head details.
                        
                        Extract the details and return them strictly in JSON format with the following keys. 
                        Keep the values concise, in English:
                        {
                            "gender": "e.g., male, female, or non-binary",
                            "hair_and_face": "detailed description of hair style, hair color, and facial facial structure/features",
                            "expression": "e.g., confident, neutral, charming smile, high-fashion intense stare",
                            "pose": "e.g., professional model runway walk, dynamic fashion stance, looking over shoulder",
                            "shot_type": "e.g., full-body fashion shot, medium-full shot",
                            "camera_angle": "e.g., eye-level, low angle hero shot",
                            "background": "e.g., minimalist concrete studio, urban street look, luxury architectural interior",
                            "art_style": "e.g., high-end fashion photography, editorial look, photorealistic, 8k resolution",
                            "lighting": "e.g., dramatic studio lighting, soft rim light"
                        }
                        Do not include any markdown formatting like ```json or text outside the JSON object.
                        """
                        
                        # Kirim list gambar yang dinamis tergantung input user
                        content_inputs = [image]
                        if face_file:
                            content_inputs.append(face_image)
                        content_inputs.append(prompt_analysis)
                        
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=content_inputs,
                        )
                        
                        st.session_state.analyzed_data = json.loads(response.text.strip())
                        st.success("Analisis gambar selesai!")
                    except Exception as e:
                        st.error(f"Gagal menganalisis gambar: {e}")

with col2:
    st.subheader("2. Modifikasi Kategori & Detail")
    
    data = st.session_state.analyzed_data if st.session_state.analyzed_data else {}
    
    def get_options(key, default_list):
        ai_value = data.get(key, "")
        if ai_value and ai_value not in default_list:
            return [ai_value] + default_list
        return default_list

    # 1. Basic Traits & Face
    genders = ["male", "female", "androgynous model"]
    selected_gender = st.selectbox("Gender", get_options("gender", genders))
    
    # Input Teks Otomatis buat detail wajah dari Gambar Kedua
    ai_face_detail = data.get("hair_and_face", "e.g., sharp jawline, messy silver hair, clean skin")
    face_detail = st.text_input("Detail Wajah & Kepala (Hasil Deteksi/Custom)", ai_face_detail)
    
    expressions = ["high-fashion intense stare", "confident smirk", "neutral editorial look", "charming warm smile", "mysterious look"]
    selected_expression = st.selectbox("Ekspresi Wajah", get_options("expression", expressions))
    
    # 2. Fitur Baru: Pose Model Busana / Fashion Poses Kekinian
    fashion_poses = [
        "professional runway walk stance",
        "asymmetric high-fashion stance",
        "candid street style walk, movement blur",
        "leaning against a textured wall, relaxed",
        "sitting elegantly on a minimalist stool",
        "hands in pockets, casual editorial pose",
        "looking back over the shoulder (back shot view)"
    ]
    selected_pose = st.selectbox("Pose Karakter / Model Busana", get_options("pose", fashion_poses))
    
    # 3. Camera & Environment
    shots = ["full-body fashion shot", "three-quarter editorial shot", "medium shot (MCU)", "close-up portrait"]
    angles = ["eye-level angle", "low angle (hero/runway look)", "high angle shot"]
    backgrounds = ["minimalist concrete studio backdrop", "urban industrial street, blurred background", "luxury modern architectural interior", "clean solid cyclorama backdrop", "cyberpunk neon alleyway"]
    
    selected_shot = st.selectbox("Shot Type", get_options("shot_type", shots))
    selected_angle = st.selectbox("Camera Angle", get_options("camera_angle", angles))
    selected_bg = st.selectbox("Background / Lokasi", get_options("background", backgrounds))
    
    # 4. Fitur Baru: Color Tone (Warm vs Cold)
    color_tones = [
        "Warm tone, golden hour sunlight, amber undertones",
        "Warm tone, soft moody terracotta palette",
        "Cold tone, cinematic cool blue color grading",
        "Cold tone, overcast winter light, desaturated tones",
        "Neutral color tone, high contrast true colors"
    ]
    selected_tone = st.selectbox("Color Tone / Mood Warna", color_tones)
    
    # 5. Style & Lighting
    styles = ["commercial fashion photography, Vogue editorial style", "photorealistic, shot on 35mm lens, 8k", "3D render, cyberpunk concept art style"]
    lightings = ["dramatic high-contrast studio lighting", "soft diffuse rim lighting", "cinematic natural lighting with soft shadows"]
    
    selected_style = st.selectbox("Art Style", get_options("art_style", styles))
    selected_lighting = st.selectbox("Lighting", get_options("lighting", lightings))
    
    extra_detail = st.text_input("Detail Tambahan (Contoh: wearing oversized trench coat, aesthetic jewelry)", "")

    st.write("---")
    st.subheader("3. Hasil Prompt Akhir")
    
    # Merangkai Prompt Terstruktur
    prompt_elements = [
        f"A professional {selected_style} of a {selected_gender}",
        f"with {face_detail}",
        f"showing a {selected_expression} expression",
        f"in a {selected_pose}",
        f"{selected_shot}, shot from a {selected_angle}",
        f"located in a {selected_bg}",
        f"with {selected_lighting}",
        f"{selected_tone}"
    ]
    
    if extra_detail:
        prompt_elements.append(extra_detail)
        
    final_prompt = ", ".join(prompt_elements) + " --ar 16:9 --v 6.0"
    
    st.text_area("Copy prompt ini ke Midjourney / Stable Diffusion / DALL-E:", final_prompt, height=140)
