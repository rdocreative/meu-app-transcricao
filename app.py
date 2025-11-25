import streamlit as st
from openai import OpenAI
import yt_dlp
import os
import tempfile

# Chave vem do secrets do Streamlit (nunca mais erro)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Transcrição com YouTube", layout="centered")
st.title("Transcrição Rápida (YouTube + Arquivo)")
st.write("Cole um link do YouTube ou faça upload de áudio/vídeo")

# === OPÇÃO 1: Link do YouTube ===
youtube_url = st.text_input("Link do YouTube (funciona com vídeos longos também)")

# === OPÇÃO 2: Upload de arquivo ===
uploaded_file = st.file_uploader("Ou faça upload de um arquivo (MP3, MP4, etc.)", 
                                 type=["mp3", "mp4", "wav", "m4a", "webm", "mov"])

file_to_transcribe = None

if youtube_url:
    with st.spinner("Baixando áudio do YouTube... (pode levar 10-30 segundos)"):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio_temp.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            audio_file = "audio_temp.wav"
            file_to_transcribe = open(audio_file, "rb")
        st.success(f"Áudio baixado: **{info['title']}**")

elif uploaded_file:
    file_to_transcribe = uploaded_file

# === Transcrição ===
if file_to_transcribe:
    with st.spinner("Transcrevendo com Whisper... (segundos a minutos)"):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=file_to_transcribe
        )
        texto = transcript.text

    st.success("Transcrição pronta!")
    st.write(texto)

    st.download_button(
        label="Baixar transcrição (.txt)",
        data=texto,
        file_name="transcricao.txt",
        mime="text/plain"
    )

    # Limpeza do arquivo temporário do YouTube
    if youtube_url and os.path.exists("audio_temp.wav"):
        os.remove("audio_temp.wav")
