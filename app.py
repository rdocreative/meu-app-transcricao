import streamlit as st
from openai import OpenAI
from pytube import YouTube
from moviepy.editor import AudioFileClip
import os
import tempfile

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Transcrição YouTube + Arquivo", layout="centered")
st.title("Transcrição com YouTube e Arquivo")
st.write("Funciona com qualquer vídeo do YouTube (público ou com restrição de idade)")

# Input do YouTube
youtube_url = st.text_input("Cole o link do YouTube aqui")

# Upload manual
uploaded_file = st.file_uploader("Ou faça upload de um arquivo", 
                                 type=["mp3", "mp4", "wav", "m4a", "webm", "mov", "avi"])

file_path = None
title = "Transcrição"

if youtube_url.strip() and not uploaded_file:
    with st.spinner("Baixando áudio do YouTube... (10-60 segundos)"):
        try:
            yt = YouTube(youtube_url)
            title = yt.title or "Vídeo do YouTube"
            st.write(f"**{title}**")
            
            # Pega o melhor áudio disponível
            stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            temp_video = stream.download(filename="temp_video.mp4")
            
            # Converte pra WAV
            audio_clip = AudioFileClip(temp_video)
            temp_wav = "temp_audio.wav"
            audio_clip.write_audiofile(temp_wav, verbose=False, logger=None)
            file_path = temp_wav
            
            st.success("Áudio baixado e convertido!")
            audio_clip.close()
            os.remove(temp_video)
            
        except Exception as e:
            st.error(f"Erro com YouTube: {str(e)}")
            st.stop()

elif uploaded_file:
    bytes_data = uploaded_file.read()
    file_path = f"temp_uploaded.{uploaded_file.name.split('.')[-1]}"
    with open(file_path, "wb") as f:
        f.write(bytes_data)
    title = uploaded_file.name

# Transcrição
if file_path:
    with st.spinner("Transcrevendo com Whisper (OpenAI)..."):
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
    if os.path.exists(file_path):
        os.remove(file_path)
