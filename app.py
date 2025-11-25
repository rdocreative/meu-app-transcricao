import streamlit as st
from openai import OpenAI
import yt_dlp
import os
import re

# Sua chave (já está no secrets)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Transcrição YouTube", layout="centered")
st.title("Transcrição de YouTube + Arquivo")
st.caption("Funciona com qualquer vídeo público ou com restrição de idade (sem precisar de cookies)")

url = st.text_input("Link do YouTube")
uploaded_file = st.file_uploader("Ou upload de áudio/vídeo", type=["mp3","mp4","wav","m4a","webm","mov","mkv"])

if url:
    with st.spinner("Baixando o melhor áudio disponível... (10-90 segundos)"):
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best[ext=mp4]/best',  # pega direto m4a ou mp4 (Whisper aceita)
            'outtmpl': 'audio',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Vídeo do YouTube')
        
        # acha o arquivo baixado
        audio_file = None
        for ext in ['m4a', 'mp4', 'webm', 'mp3']:
            if os.path.exists(f"audio.{ext}"):
                audio_file = f"audio.{ext}"
                break
        if not audio_file and os.path.exists("audio"):
            audio_file = "audio"

    if audio_file and os.path.exists(audio_file):
        with st.spinner("Transcrevendo com Whisper..."):
            with open(audio_file, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            texto = transcript.text

        st.success("Transcrição pronta!")
        st.subheader(title)
        st.write(texto)
        st.download_button("Baixar (.txt)", texto, f"{title[:50].replace(' ', '_')}_transcricao.txt")
        
        # limpa
        if os.path.exists(audio_file):
            os.remove(audio_file)
    else:
        st.error("Erro ao baixar o áudio")

elif uploaded_file:
    with st.spinner("Transcrevendo com Whisper..."):
        transcript = client.audio.transcriptions.create(model="whisper-1", file=uploaded_file)
    st.success("Pronto!")
    st.write(transcript.text)
    st.download_button("Baixar", transcript.text, "transcricao.txt")
