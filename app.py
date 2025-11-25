import streamlit as st
from openai import OpenAI
import yt_dlp
import os

# Chave da OpenAI via secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Maestra.ai", layout="centered")
st.title("🎙️ Maestra.ai - Transcrição de YouTube")
st.caption("Vídeo do YouTube → Transcrição perfeita | Agora com login anti-bot (cookies)")

url = st.text_input("Cole o link do YouTube aqui", placeholder="https://www.youtube.com/watch?v=...")
uploaded_file = st.file_uploader(
    "Ou faça upload direto de áudio/vídeo",
    type=["mp3", "mp4", "wav", "m4a", "webm", "mov", "mkv", "avi", "ogg"]
)

# =============================================
# DOWNLOAD DO YOUTUBE (com cookies anti-bot)
# =============================================
if url:
    with st.spinner("Autenticando e baixando áudio... (10-90 segundos)"):
        # Carrega cookies se o arquivo existir (bypassa bot check)
        cookies_path = "cookies.txt"
        if os.path.exists(cookies_path):
            st.caption("✅ Cookies carregados (anti-bot ativo)")
        else:
            st.warning("⚠️ Cookies não encontrados — teste com vídeo público ou adicione cookies.txt")

        ydl_opts = {
            'format': 'bestaudio/best',           # Melhor áudio
            'outtmpl': 'audio.%(ext)s',           # Nome com extensão
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'cookies': cookies_path if os.path.exists(cookies_path) else None,  # ← AQUI: autenticação
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # ← User-agent humano
            'postprocessors': [{                  # Extrai áudio com FFmpeg
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
            st.error("❌ Erro no download (pode ser bot check ou vídeo privado).")
            st.caption("Solução: Adicione cookies.txt ou teste vídeo público como https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            st.exception(e)
            audio_file = None

    # =============================================
    # TRANSCRIÇÃO
    # =============================================
    if audio_file and os.path.exists(audio_file):
        with st.spinner("Transcrevendo com Whisper-1..."):
            with open(audio_file, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="pt"  # Melhora pra português
                )
            texto = transcript.text

        st.success("✅ Transcrição pronta! 🎉")
        st.subheader(f"📹 {title}")
        st.write(texto)
        st.download_button(
            "📥 Baixar (.txt)",
            texto,
            file_name=f"{title[:60].replace(' ', '_')}_transcricao.txt",
            mime="text/plain"
        )

        # Limpa arquivo
        try:
            os.remove(audio_file)
        except:
            pass

    elif audio_file is None:
        st.error("Falha no download.")

# =============================================
# UPLOAD MANUAL
# =============================================
elif uploaded_file:
    with st.spinner("Transcrevendo upload..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=uploaded_file
        )
    texto = transcript.text
    st.success("✅ Pronto!")
    st.write(texto)
    st.download_button(
        "📥 Baixar",
        texto,
        file_name="transcricao.txt",
        mime="text/plain"
    )

st.markdown("---")
st.caption("Maestra.ai 2025 | Whisper + yt-dlp | Cookies by https://github.com/yt-dlp/yt-dlp")
