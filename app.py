import streamlit as st
from openai import OpenAI
import yt_dlp
import os

# Chave da OpenAI via secrets (agora funciona de verdade)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Maestra.ai", layout="centered")
st.title("🎙️ Maestra.ai - Transcrição de YouTube")
st.caption("Vídeo do YouTube → Transcrição perfeita em segundos | Funciona com restrição de idade · Shorts · Lives arquivadas")

url = st.text_input("Cole o link do YouTube aqui", placeholder="https://www.youtube.com/watch?v=...")
uploaded_file = st.file_uploader(
    "Ou faça upload direto de áudio/vídeo",
    type=["mp3", "mp4", "wav", "m4a", "webm", "mov", "mkv", "avi", "ogg"]
)

# =============================================
# DOWNLOAD DO YOUTUBE (com FFmpeg garantido)
# =============================================
if url:
    with st.spinner("Baixando o áudio do vídeo... (10-90 segundos)"):
        ydl_opts = {
            'format': 'bestaudio/best',           # Pega o melhor áudio disponível
            'outtmpl': 'audio.%(ext)s',           # Nome com extensão correta
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'postprocessors': [{                  # ← AQUI ESTÁ A MÁGICA (usa o ffmpeg que você instalou)
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',          # mp3 é 100% compatível com Whisper
                'preferredquality': '192',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Vídeo do YouTube')
            audio_file = "audio.mp3"  # Sempre será esse nome agora

        except Exception as e:
            st.error("Não foi possível baixar o áudio desse vídeo.")
            st.caption("Tente outro link ou faça upload manual.")
            st.exception(e)
            audio_file = None

    # =============================================
    # TRANSCRIÇÃO COM WHISPER
    # =============================================
    if audio_file and os.path.exists(audio_file):
        with st.spinner("Transcrevendo com Whisper-1 (OpenAI)..."):
            with open(audio_file, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="pt"  # opcional: força detecção em português (melhora acertos)
                )
            texto = transcript.text

        st.success("Transcrição concluída! 🎉")
        st.subheader(f"📹 {title}")
        st.write(texto)
        st.download_button(
            "📥 Baixar transcrição (.txt)",
            texto,
            file_name=f"{title[:60].replace(' ', '_')}_transcricao.txt",
            mime="text/plain"
        )

        # Limpa o arquivo temporário
        try:
            os.remove(audio_file)
        except:
            pass

    elif audio_file is None:
        st.error("Falha no download do áudio.")

# =============================================
# UPLOAD MANUAL (funciona sempre)
# =============================================
elif uploaded_file:
    with st.spinner("Transcrevendo arquivo enviado..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=uploaded_file
        )
    texto = transcript.text
    st.success("Pronto!")
    st.write(texto)
    st.download_button(
        "📥 Baixar transcrição",
        texto,
        file_name="transcricao.txt",
        mime="text/plain"
    )

# =============================================
# RODAPÉ
# =============================================
st.markdown("---")
st.caption("Maestra.ai feito com ❤️ por você · Whisper-1 + yt-dlp + Streamlit · 2025")
