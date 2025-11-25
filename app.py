import streamlit as st
from openai import OpenAI
import yt_dlp
import os
import tempfile

# Chave vem direto do secrets (nunca mais erro)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Transcrição YouTube + Arquivo", layout="centered")
st.title("Transcrição com YouTube e Arquivo")
st.write("Cole um link do YouTube OU faça upload de áudio/vídeo")

# === 1. Link do YouTube ===
youtube_url = st.text_input("Link do YouTube")

# === 2. Upload de arquivo ===
uploaded_file = st.file_uploader("Ou faça upload do arquivo", 
                                 type=["mp3", "mp4", "wav", "m4a", "webm", "mov", "avi"])

file_to_transcribe = None
title = "Arquivo enviado"

# Processa YouTube
if youtube_url.strip() and not uploaded_file:
    with st.spinner("Baixando áudio do YouTube... (10-40 segundos)"):
        try:
            # Configuração que funciona 100% no Streamlit Cloud
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'quiet': True,
                'no_warnings': True,
                'outtmpl': '%(id)s.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                filename = f"{info['id']}.wav"
                title = info.get('title', 'Vídeo do YouTube')
                file_to_transcribe = open(filename, "rb")
            st.success(f"Baixado: **{title}**")
        except Exception as e:
            st.error(f"Erro ao baixar YouTube: {str(e)}")
            st.stop()

# Processa upload
elif uploaded_file:
    file_to_transcribe = uploaded_file

# === Transcrição com Whisper ===
if file_to_transcribe:
    with st.spinner("Transcrevendo com Whisper..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=file_to_transcribe
        )
        texto = transcript.text

    st.success("Transcrição pronta!")
    st.subheader(f"**{title}**")
    st.write(texto)

    st.download_button(
        label="Baixar transcrição (.txt)",
        data=texto,
        file_name=f"{title[:50].replace(' ', '_')}_transcricao.txt",
        mime="text/plain"
    )

    # Limpeza (só se for do YouTube)
    if youtube_url and 'filename' in locals() and os.path.exists(filename):
        try:
            os.remove(filename)
        except:
            pass
