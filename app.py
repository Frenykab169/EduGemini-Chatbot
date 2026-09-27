"""
EduGemini AI - Asisten Belajar & Tutor Interaktif Berbasis Gemini API
Final Project: LLM-Based Tools and Gemini API Integration for Data Scientists (Hacktiv8)
Author: Student of Hacktiv8 Data Science Program
"""

import streamlit as st
import os
import json
from datetime import datetime

# -----------------------------------------------------------------------------
# KONFIGURASI HALAMAN STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EduGemini AI - Asisten Belajar Cerdas",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi Google Generative AI secara dinamis / aman
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# -----------------------------------------------------------------------------
# DEFINISI DOMAIN, GAYA BAHASA & SYSTEM PROMPT
# -----------------------------------------------------------------------------
PERSONAS = {
    "Data Science & AI Mentor": {
        "icon": "🤖",
        "desc": "Ahli Machine Learning, Python, Statistik, dan Rekayasa Prompt.",
        "prompt": "Anda adalah Senior Data Scientist dan Mentor AI di Hacktiv8. Tugas Anda adalah membimbing pengguna belajar Data Science, Machine Learning, Deep Learning, statistik, dan pemrograman Python dengan penjelasan yang runtut, berbasis contoh nyata, dan kode yang bersih."
    },
    "Tutor Matematika & Sains": {
        "icon": "📐",
        "desc": "Spesialis pemecahan rumus matematika, fisika, dan logika terstruktur.",
        "prompt": "Anda adalah Tutor Ahli Matematika dan Sains. Bantu pengguna menyelesaikan soal perhitungan, menurunkan rumus matematis, serta menjelaskan konsep fisika/sains langkah demi langkah secara logis."
    },
    "Asisten Pemrograman & Software Dev": {
        "icon": "💻",
        "desc": "Spesialis coding (Python, JavaScript, SQL), debugging, dan arsitektur.",
        "prompt": "Anda adalah Software Engineer Senior. Bantu pengguna menulis kode efisien, menemukan bug (debugging), menjelaskan struktur data & algoritma, serta best practices pemrograman."
    },
    "Tutor Bahasa & Penulisan Akademis": {
        "icon": "✍️",
        "desc": "Pakar tata bahasa, struktur esai, penulisan jurnal, dan terjemahan.",
        "prompt": "Anda adalah Dosen Bahasa dan Penulisan Akademis. Bantu pengguna menyusun esai, memeriksa tata bahasa, memperkaya kosakata, serta menyusun argumen akademis yang meyakinkan."
    },
    "Study Buddy & Motivator Belajar": {
        "icon": "🌟",
        "desc": "Pendamping belajar ramah, manajemen waktu, dan perencana jadwal.",
        "prompt": "Anda adalah Study Buddy yang suportif dan antusias. Bantu pengguna membagi topik belajar menjadi sub-target harian, memberikan kuis interaktif, dan menjaga motivasi belajar."
    }
}

TONES = {
    "Santai & Gaul (Friendly Mentor)": "Gunakan gaya bahasa santai, kasual, bersahabat, seperti mengobrol dengan rekan belajar yang asyik namun tetap informatif dan sopan.",
    "Formal Akademis": "Gunakan bahasa Indonesia baku yang formal, terstruktur, berbasis data ilmiah, dan bernada akademis.",
    "Sederhana & Ramah Pemula (ELI5)": "Jelaskan dengan analogi kehidupan sehari-hari, bahasa yang sangat sederhana, tanpa jargon rumit sehingga anak berusia 10 tahun atau pemula dapat langsung paham.",
    "Ringkas & To-The-Point (Executive Summary)": "Berikan jawaban padat, langsung pada intinya dalam poin-poin terstruktur tanpa pengantar berbelit-belit."
}

SAMPLE_PROMPTS = {
    "Data Science & AI Mentor": [
        "Jelaskan perbedaan Supervised vs Unsupervised Learning secara intuitif.",
        "Bagaimana cara menangani data imbalance (SMOTE vs Class Weight) di Python?",
        "Tuliskan fungsi Python untuk menghitung metrik akurasi, precision, recall, dan F1-Score."
    ],
    "Tutor Matematika & Sains": [
        "Bagaimana cara menurunkan rumus turunan fungsi f(x) = x^3 - 4x + 7?",
        "Jelaskan konsep Teorema Bayes dengan analogi tes diagnostik medis.",
        "Mengapa langit berwarna biru? Jelaskan fenomena hamburan Rayleigh."
    ],
    "Asisten Pemrograman & Software Dev": [
        "Bagaimana cara kerja API RESTful dan apa perbedaan metode GET vs POST?",
        "Bantu saya membuat query SQL untuk mencari 5 pelanggan dengan transaksi tertinggi.",
        "Jelaskan konsep Asynchronous Programming di JavaScript/Python."
    ],
    "Tutor Bahasa & Penulisan Akademis": [
        "Bantu saya menyusun paragraf pendahuluan esai tentang dampak Generative AI.",
        "Koreksi kalimat berikut agar lebih efektif dan baku sesuai EYD.",
        "Bagaimana cara membuat abstrak penelitian yang memuat latar belakang, metode, dan hasil?"
    ],
    "Study Buddy & Motivator Belajar": [
        "Buatkan jadwal belajar 7 hari untuk menguasai dasar-dasar Library Pandas & NumPy.",
        "Berikan saya 3 kuis logika ringan untuk menguji pemahaman saya hari ini.",
        "Bagaimana cara mengatasi rasa malas (prokrastinasi) saat deadline tugas akhir?"
    ]
}

# -----------------------------------------------------------------------------
# SIDEBAR KONFIGURASI PARAMETER KREATIF
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bot.png", width=64)
    st.title("⚙️ Parameter Kreatif")
    st.caption("LLM-Based Tools & Gemini API Integration")

    st.markdown("---")
    
    # 1. API Key Setup
    api_key = st.text_input(
        "🔑 Gemini API Key:",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="Dapatkan API Key gratis di Google AI Studio (aistudio.google.com)"
    )

    # 2. Pilihan Model
    model_name = st.selectbox(
        "🧠 Pilihan Model LLM:",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"],
        index=0,
        help="gemini-1.5-flash: Cepat dan efisien. gemini-1.5-pro: Penalaran kompleks tingkat tinggi."
    )

    # 3. Domain Pengetahuan / Persona
    selected_persona_key = st.selectbox(
        "🎯 Domain Pengetahuan & Persona:",
        list(PERSONAS.keys()),
        index=0
    )
    current_persona = PERSONAS[selected_persona_key]
    st.info(f"{current_persona['icon']} **{selected_persona_key}**\n\n{current_persona['desc']}")

    # 4. Gaya Bahasa / Tone
    selected_tone_key = st.selectbox(
        "🗣️ Gaya Bahasa (Tone of Voice):",
        list(TONES.keys()),
        index=0
    )
    current_tone = TONES[selected_tone_key]

    st.markdown("---")
    st.subheader("🎛️ LLM Hyperparameters")

    # 5. Temperature (Kreativitas vs Determinisme)
    temperature = st.slider(
        "🌡️ Temperature (Kreativitas):",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help="Nilai rendah (0.1 - 0.3) = Jawaban presisi & matematis. Nilai tinggi (0.7 - 1.0) = Lebih kreatif & bervariasi."
    )

    # 6. Max Output Tokens
    max_tokens = st.slider(
        "📏 Max Output Tokens:",
        min_value=256,
        max_value=4096,
        value=2048,
        step=256,
        help="Batas maksimal panjang respon AI."
    )

    st.markdown("---")
    # 7. Manajemen Riwayat & Reset
    col_reset, col_export = st.columns(2)
    with col_reset:
        if st.button("🗑️ Hapus Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# -----------------------------------------------------------------------------
# INITIALISASI STATE PERCAKAPAN (CONVERSATION MEMORY)
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Halo! Saya **EduGemini AI**, asisten belajar cerdas Anda. Saat ini saya berperan sebagai **{selected_persona_key}** dengan gaya bahasa **{selected_tone_key}**.\n\nApa konsep, materi, atau tugas yang ingin Anda pelajari atau diskusikan hari ini?",
            "timestamp": datetime.now().strftime("%H:%M")
        }
    ]

# -----------------------------------------------------------------------------
# AREA UTAMA CHATBOT
# -----------------------------------------------------------------------------
st.title("🎓 EduGemini AI: Smart Learning Companion")
st.markdown(
    f"**Mode Aktif:** `{current_persona['icon']} {selected_persona_key}` | "
    f"**Gaya:** `{selected_tone_key}` | "
    f"**Model:** `{model_name}` (Temp: `{temperature}`)"
)

# Widget Rekomendasi Prompt (Quick Suggestion Pills)
st.markdown("💡 **Rekomendasi Pertanyaan Cepat:**")
cols = st.columns(3)
quick_prompts = SAMPLE_PROMPTS.get(selected_persona_key, [])
for idx, prompt_text in enumerate(quick_prompts):
    with cols[idx % 3]:
        if st.button(f"📌 {prompt_text}", key=f"quick_{idx}", use_container_width=True):
            st.session_state.user_input_preset = prompt_text
            st.rerun()

st.markdown("---")

# Tampilkan Seluruh Riwayat Pesan (Memory Display)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(msg["content"])
            st.caption(f"Dikirim pada {msg.get('timestamp', '')}")
    else:
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(msg["content"])
            st.caption(f"EduGemini ({model_name}) • {msg.get('timestamp', '')}")

# -----------------------------------------------------------------------------
# FUNGSI INTERAKSI DENGAN GEMINI API / FALLBACK MOCK
# -----------------------------------------------------------------------------
def generate_response(prompt_text, history_messages):
    full_system_instruction = (
        f"{current_persona['prompt']}\n\n"
        f"ATURAN GAYA BAHASA:\n{current_tone}\n\n"
        "Gunakan format Markdown lengkap dengan bullet point, rumus matematika (LaTeX), "
        "dan code-block yang terstruktur rapi bila menjelaskan konsep teknis."
    )

    # 1. Jika API Key ada dan library terpasang, gunakan Gemini API Asli
    if api_key and HAS_GENAI:
        try:
            genai.configure(api_key=api_key)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": 0.95
            }
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=full_system_instruction
            )

            # Bangun context memory dari history percakapan
            gemini_history = []
            for m in history_messages[:-1]: # exclude prompt yang baru
                role_mapped = "user" if m["role"] == "user" else "model"
                gemini_history.append({"role": role_mapped, "parts": [m["content"]]})

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt_text)
            return response.text
        except Exception as e:
            return f"⚠️ **Error Gemini API:** {str(e)}\n\n*Silakan periksa apakah Gemini API Key Anda valid dan memiliki kuota yang cukup.*"

    # 2. Mock / Demo Response Cerdas jika belum ada API Key (Mencegah Error saat Review)
    else:
        now_str = datetime.now().strftime("%H:%M:%S")
        simulated_header = "*(Mode Simulasi Interaktif - Masukkan Gemini API Key di sidebar untuk koneksi live Gemini)*\n\n"
        
        if "supervised" in prompt_text.lower() or "machine learning" in prompt_text.lower():
            return (
                simulated_header +
                f"### Penjelasan Supervised vs Unsupervised Learning\n\n"
                f"Halo rekan pembelajar! Senang sekali membahas topik dasar Data Science ini.\n\n"
                f"1. **Supervised Learning (Pembelajaran Terawasi):**\n"
                f"   - **Konsep:** Model dilatih menggunakan data yang memiliki **label/target** (ground truth).\n"
                f"   - **Analogi:** Seperti murid yang belajar soal ujian yang sudah ada kunci jawabannya.\n"
                f"   - **Contoh Kasus:** Klasifikasi email Spam/Bukan Spam, Regresi prediksi harga rumah.\n\n"
                f"2. **Unsupervised Learning (Pembelajaran Tanpa Pengawasan):**\n"
                f"   - **Konsep:** Model diberikan data **tanpa label**, tujuannya mencari pola tersembunyi (*clusters* atau *associations*).\n"
                f"   - **Analogi:** Mengelompokkan barang belanjaan supermarket berdasarkan kemiripan kebiasaan pembeli.\n"
                f"   - **Contoh Kasus:** Segmentasi pelanggan (K-Means), reduksi dimensi (PCA).\n\n"
                f"```python\n# Contoh Singkat Scikit-Learn\nfrom sklearn.cluster import KMeans\nkmeans = KMeans(n_clusters=3, random_state=42)\nkmeans.fit(X_customer_data)\n```\n\n"
                f"Ada bagian yang ingin kita bedah lebih dalam?"
            )
        elif "turunan" in prompt_text.lower() or "rumus" in prompt_text.lower():
            return (
                simulated_header +
                f"### Penyelesaian Turunan Matematis f(x)\n\n"
                f"Diberikan fungsi: $$f(x) = x^3 - 4x + 7$$\n\n"
                f"**Langkah Penyelesaian Menggunakan Aturan Pangkat (Power Rule):**\n"
                f"$$\\frac{d}{dx}[x^n] = n \\cdot x^{{n-1}}$$\n\n"
                f"1. Turunan dari $x^3$ adalah $3x^{{3-1}} = 3x^2$\n"
                f"2. Turunan dari $-4x$ adalah $-4(1) = -4$\n"
                f"3. Turunan dari konstanta $+7$ adalah $0$\n\n"
                f"**Hasil Akhir:**\n"
                f"$$f'(x) = 3x^2 - 4$$\n\n"
                f"Apakah Anda ingin melanjutkan dengan mencari titik stasioner ($f'(x) = 0$)?"
            )
        else:
            return (
                simulated_header +
                f"### Respon EduGemini AI ({selected_persona_key})\n\n"
                f"Terima kasih atas pertanyaannya: *\"{prompt_text}\"*\n\n"
                f"Sebagai **{selected_persona_key}**, pendekatan terbaik untuk memahami hal ini adalah:\n"
                f"- **Langkah 1:** Memahami konsep fundamental dan definisi intinya.\n"
                f"- **Langkah 2:** Mengaitkannya dengan studi kasus di industri nyata.\n"
                f"- **Langkah 3:** Melakukan latihan terstruktur (praktik mandiri).\n\n"
                f"💡 *Catatan Pengajar:* Parameter aktif saat ini: Temperature `{temperature}` dengan gaya bahasa `{selected_tone_key}`."
            )

# -----------------------------------------------------------------------------
# INPUT CHAT DARI PENGGUNA
# -----------------------------------------------------------------------------
default_prompt = st.session_state.pop("user_input_preset", "")
user_prompt = st.chat_input("Ketik pertanyaan atau topik belajar Anda di sini...", key="chat_input_box")

# Dukungan bila user mengklik tombol quick prompt
if not user_prompt and default_prompt:
    user_prompt = default_prompt

if user_prompt:
    now_time = datetime.now().strftime("%H:%M")
    
    # 1. Simpan pesan pengguna ke state memory
    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt,
        "timestamp": now_time
    })
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)
        st.caption(f"Dikirim pada {now_time}")

    # 2. Hasilkan respon AI
    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("EduGemini sedang menganalisis & merumuskan jawaban..."):
            ai_reply = generate_response(user_prompt, st.session_state.messages)
            st.markdown(ai_reply)
            st.caption(f"EduGemini ({model_name}) • {now_time}")

    # 3. Simpan respon AI ke state memory
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_reply,
        "timestamp": now_time
    })

# -----------------------------------------------------------------------------
# FITUR EXPORT PERCAKAPAN
# -----------------------------------------------------------------------------
with col_export:
    chat_export_text = f"# EduGemini AI - Transkrip Percakapan\n"
    chat_export_text += f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    chat_export_text += f"Persona: {selected_persona_key} | Gaya: {selected_tone_key} | Model: {model_name}\n\n---\n\n"
    for m in st.session_state.messages:
        role_label = "Pengguna" if m["role"] == "user" else "EduGemini AI"
        chat_export_text += f"### {role_label} ({m.get('timestamp', '')}):\n{m['content']}\n\n"
    
    st.download_button(
        label="📥 Ekspor Chat (.md)",
        data=chat_export_text,
        file_name=f"EduGemini_Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown",
        use_container_width=True
    )
