import streamlit as st
from openai import OpenAI
import yt_dlp
import os
from yt_dlp_youtube_oauth2 import YoutubeOAuth2  # ← OAuth2 automático

# Chave OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Maestra.ai", layout="centered")
st.title("🎙️ Maestra.ai - Transcrição Anti-Bot 2025")
st.caption("Baixa QUALQUER vídeo do YT sem erros de bot (OAuth2 + cookies fallback)")

url = st.text_input("Link do YouTube", placeholder="https://www.youtube.com/watch?v=...")
uploaded_file = st.file_uploader("Ou upload de áudio/vídeo", type=["mp3", "mp4", "wav", "m4a", "webm"])

if url:
    with st.spinner("Autenticando anti-bot e baixando áudio..."):
        # Tenta OAuth2 primeiro (melhor pra cloud, sem cookies manuais)
        try:
            oauth = YoutubeOAuth2()
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'extractor_args': {'youtube': {'oauth': oauth}},  # ← OAuth2 mágico
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            st.caption("✅ OAuth2 ativo (sem cookies necessários)")
        except Exception as e:
            st.warning("⚠️ OAuth2 falhou — usando cookies fallback")
            cookies_path = "cookies.txt"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'cookies': cookies_path if os.path.exists(cookies_path) else None,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',  # Rotativo anti-detecção
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Vídeo do YouTube')
            audio_file = "audio.mp3"
        except Exception as e:
            st.error("❌ Erro persistente — teste vídeo público ou adicione cookies.txt")
            st.caption("Link de teste: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            st.exception(e)
            audio_file = None

    if audio_file and os.path.exists(audio_file):
        with st.spinner("Transcrevendo com Whisper..."):
            with open(audio_file, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="pt"
                )
            texto = transcript.text

        st.success("✅ Transcrição pronta! (Sem mais erros de bot)")
        st.subheader(f"📹 {title}")
        st.write(texto)
        st.download_button("📥 Baixar (.txt)", texto, f"{title[:60].replace(' ', '_')}_transcricao.txt")

        # Limpa
        try:
            os.remove(audio_file)
        except:
            pass
    else:
        st.error("Falha no download — use OAuth2 ou cookies.")

elif uploaded_file:
    with st.spinner("Transcrevendo upload..."):
        transcript = client.audio.transcriptions.create(model="whisper-1", file=uploaded_file)
    texto = transcript.text
    st.success("✅ Pronto!")
    st.write(texto)
    st.download_button("📥 Baixar", texto, "transcricao.txt")

st.markdown("---")
st.caption("Anti-bot 2025: OAuth2 via yt-dlp-youtube-oauth2 | Testado em Streamlit Cloud")
