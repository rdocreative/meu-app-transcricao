import streamlit as st
from openai import OpenAI
import yt_dlp
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Maestra.ai", layout="centered")
st.title("Maestra.ai – Transcrição YouTube")
st.caption("Funciona com vídeos públicos e +18 · 2025")

url = st.text_input("Link do YouTube")
uploaded_file = st.file_uploader("Ou upload de arquivo", type=["mp3","mp4","wav","m4a","webm","mov"])

if url:
    with st.spinner("Baixando áudio..."):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'referer': 'https://www.youtube.com/',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Vídeo')
            audio_file = "audio.mp3"
            st.success("Download concluído")
        except:
            st.error("Vídeo bloqueado ou privado. Use upload manual ou link público.")
            audio_file = None

    if audio_file and os.path.exists(audio_file):
        with st.spinner("Transcrevendo..."):
            with open(audio_file, "rb") as f:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
            texto = transcript.text
        st.success("Pronto!")
        st.subheader(title)
        st.write(texto)
        st.download_button("Baixar .txt", texto, f"{title[:50]}_transcricao.txt")
        os.remove(audio_file)

elif uploaded_file:
    with st.spinner("Transcrevendo..."):
        transcript = client.audio.transcriptions.create(model="whisper-1", file=uploaded_file)
    texto = transcript.text
    st.success("Pronto!")
    st.write(texto)
    st.download_button("Baixar .txt", texto, "transcricao.txt")
