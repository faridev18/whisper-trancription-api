import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Whisper Transcription", page_icon="🎙️")
st.title("🎙️ Whisper Transcription")
st.write("Upload un fichier audio pour le transcrire avec Whisper.")

uploaded_file = st.file_uploader(
    "Choisis un fichier audio",
    type=["mp3", "wav", "m4a", "ogg", "flac", "webm"],
)

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Transcrire"):
        with st.spinner("Transcription en cours..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_URL}/transcribe", files=files)
                response.raise_for_status()
                data = response.json()

                st.success(f"Langue détectée : **{data['language']}**")
                st.text_area("Transcription", data["text"], height=300)
            except requests.ConnectionError:
                st.error("Impossible de se connecter à l'API. Lance d'abord : `uvicorn main:app --reload --port 8000`")
            except Exception as e:
                st.error(f"Erreur : {e}")
