import streamlit as st
from openai import OpenAI
import yt_dlp
import os

# Chave do secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Transcrição YouTube", layout="centered")
st.title("Transcrição de YouTube + Arquivo")
st.write("Funciona com qualquer vídeo do YouTube (público ou com restrição de idade)")

# Input YouTube
youtube_url = st.text_input("Cole o link do YouTube")

# Upload manual
uploaded_file = st.file_uploader("Ou faça upload de um arquivo", 
                                 type=["mp3", "mp4", "wav", "m4a", "webm", "mov"])

file_path = None
title = "Transcrição"

if youtube_url and not uploaded_file:
    with st.spinner("Baixando áudio do YouTube... (10-60 segundos)"):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'outtmpl': 'temp_audio',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                title = info.get('title', 'Vídeo do YouTube')
                file_path = "temp_audio.mp3"
            st.success(f"Baixado: **{title}**")
        except Exception as e:
            st.error(f"Erro: {str(e)}")
            st.stop()

elif uploaded_file:
    bytes_data = uploaded_file.read()
    file_path = f"uploaded_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(bytes_data)
    title = uploaded_file.name

# Transcrição
if file_path and os.path.exists(file_path):
    with st.spinner("Transcrevendo com Whisper..."):
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        texto = transcript.text

    st.success("Transcrição pronta!")
    st.subheader(title)
    st.write(texto)
    
    st.download_button(
        label="Baixar transcrição (.txt)",
        data=texto,
        file_name=f"{title[:50].replace(' ', '_')}_transcricao.txt",
        mime="text/plain"
    )
    
    # Limpeza
    try:
        os.remove(file_path)
    except:
        pass
