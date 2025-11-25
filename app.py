import streamlit as st
from openai import OpenAI
from googleapiclient.discovery import build
import yt_dlp
import os
import re

# Chaves
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_API_KEY"])

st.set_page_config(page_title="Transcrição YouTube + Arquivo", layout="centered")
st.title("Transcrição de YouTube + Arquivo")
st.caption("Funciona com qualquer vídeo (público, restrito ou privado por link)")

# Input
url = st.text_input("Link do YouTube")
uploaded_file = st.file_uploader("Ou upload de áudio/vídeo", type=["mp3","mp4","wav","m4a","webm","mov"])

def extract_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

if url:
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Link inválido")
        st.stop()

    with st.spinner("Tentando legendas oficiais..."):
        try:
            captions = youtube.captions().list(part="snippet", videoId=video_id).execute()
            if captions.get("items"):
                caption_track = max(captions["items"], key=lambda x: x["snippet"]["trackKind"] == "standard" or x["snippet"]["language"] == "pt")
                download = youtube.captions().download(id=caption_track["id"], tfmt="srt").execute()
                texto = download.decode('utf-8')
                # Remove timestamps e números
                texto_limpo = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> .*?\n', '', texto)
                texto_limpo = re.sub(r'\n+', '\n', texto_limpo).strip()
                
                st.success("Legendas oficiais encontradas!")
                st.write(texto_limpo)
                st.download_button("Baixar (.txt)", texto_limpo, f"{video_id}_oficial.txt")
                st.stop()
        except:
            st.info("Sem legendas oficiais → usando Whisper (mais preciso)")

    # Fallback: Whisper via yt-dlp
    with st.spinner("Baixando áudio com Whisper... (10-90 segundos)"):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}],
            'outtmpl': 'audio',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Vídeo')
        audio_file = "audio.mp3"

    with st.spinner("Transcrevendo com Whisper..."):
        with open(audio_file, "rb") as f:
            transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=f)
        texto = transcript.text

    st.success("Transcrição pronta!")
    st.subheader(title)
    st.write(texto)
    st.download_button("Baixar (.txt)", texto, f"{title[:50]}_whisper.txt")
    os.remove(audio_file)

elif uploaded_file:
    with st.spinner("Transcrevendo com Whisper..."):
        transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=uploaded_file)
    st.success("Pronto!")
    st.write(transcript.text)
    st.download_button("Baixar", transcript.text, "transcricao.txt")
