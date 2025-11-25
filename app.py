import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Carrega API key de forma segura (do secrets.toml no deploy)
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY') or st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

st.title("Transcrição Rápida de Áudio/Vídeo com Whisper (como Maestra.ai)")

# Opção 1: Upload de arquivo (vídeo ou áudio)
uploaded_file = st.file_uploader("Faça upload de um vídeo ou áudio (MP3, MP4, etc.)", type=["mp3", "mp4", "wav", "m4a"])

# Opção 2: Gravação ao vivo
audio_record = st.audio_input("Ou grave áudio diretamente")

if uploaded_file or audio_record:
    file_to_transcribe = uploaded_file or audio_record
    
    # Transcrição rápida
    with st.spinner("Transcrevendo... (leva segundos)"):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",  # Modelo rápido e preciso, suporta 100+ idiomas
            file=file_to_transcribe
        )
        text = transcript.text
    
    st.write("Transcrição:")
    st.write(text)
    
    # Download do texto
    st.download_button(
        label="Baixar Transcrição como TXT",
        data=text,
        file_name="transcricao.txt",
        mime="text/plain"
    )

# Dica extra: Para tradução (se áudio não for em inglês)
if st.checkbox("Traduzir para Inglês?"):
    if uploaded_file or audio_record:
        translate = client.audio.translations.create(
            model="whisper-1",
            file=file_to_transcribe
        )
        st.write("Tradução:")
        st.write(translate.text)
        st.download_button(
            label="Baixar Tradução como TXT",
            data=translate.text,
            file_name="traducao.txt",
            mime="text/plain"
        )