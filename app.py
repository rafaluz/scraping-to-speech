# scraping_to_speech/app.py

import streamlit as st
import time
import os
import shutil
from utils.scraper import gerar_audio_partes, limpar_audios
from zipfile import ZipFile

st.set_page_config(page_title="Scraping to Speech", layout="wide")
st.title("🎙️ Scraping to Speech")

# Estado da sessão
if "arquivos" not in st.session_state:
    st.session_state.arquivos = []

# Lista de vozes disponíveis
vozes_disponiveis = [
    "Alloy", "Ash", "Ballad", "Coral", "Echo", "Fable",
    "Onyx", "Nova", "Sage", "Shimmer", "Verse"
]


# Inputs do usuário organizados lado a lado
col1, col2 = st.columns([3, 2])
with col1:
    prompt = st.text_area("📝 Prompt", height=400)
with col2:
    instructions = st.text_area("🧭 Instructions", value="""
Voice Style:
Grave, fluida e expressiva, com entonações que reforçam os pontos de maior impacto. Voz firme, como a de um repórter experiente, que passa autoridade e clareza ao narrar fatos relevantes. Deve transmitir seriedade, mas também indignação contida nos momentos certos, tocando o espectador com emoção genuína, sem exageros.

Sotaque:
Brasileiro, com leve sotaque do Nordeste, preferencialmente do Piauí, conferindo autenticidade e conexão popular à narrativa.

Punctuation:
Pontuação clara, com pausas estratégicas que reforcem a compreensão e a gravidade dos temas tratados. As pausas devem valorizar nomes, números e dados impactantes.

Delivery:
Sólido, direto e envolvente. Deve manter um ritmo constante, com variações naturais para destacar trechos mais graves ou emocionantes. A voz deve segurar a atenção do público como uma reportagem de TV que revela um escândalo nacional.

Phrasing:
Objetivo, com linguagem acessível, mas firme. Evitar jargões técnicos, priorizando expressões de fácil compreensão. Quando necessário, incluir frases que provoquem reflexão ou indignação no ouvinte.

Tone:
Sério e engajado, transmitindo o peso das denúncias com responsabilidade e humanidade. De tempos em tempos, uma leve emoção na voz deve refletir empatia pelas vítimas e urgência na cobrança de justiça.
""", height=400)

# voice = st.text_input("🎤 Voice (default: Ash)", value="Ash")
voice = st.selectbox("🎤 Escolha a voz", options=vozes_disponiveis, index=1)


if st.button("🔊 Gerar Voz"):
    if prompt.strip() == "":
        st.error("O prompt não pode estar vazio.")
    else:
        limpar_audios()
        with st.spinner("Gerando áudio..."):
            arquivos = gerar_audio_partes(prompt, instructions, voice)
        if arquivos:
            st.session_state.arquivos = arquivos
            st.success("✅ Áudios gerados com sucesso!")
        else:
            st.error("Não foi possível gerar os áudios.")

# Mostrar áudios e botão de download zip
if st.session_state.arquivos:
    for arquivo in st.session_state.arquivos:
        st.audio(arquivo)

    zip_path = "audios_gerados.zip"
    with ZipFile(zip_path, 'w') as zipf:
        for i, arquivo in enumerate(st.session_state.arquivos, 1):
            zipf.write(arquivo, arcname=f"audio{i}.wav")

    with open(zip_path, "rb") as f:
        st.download_button("📦 Baixar todos os áudios", data=f, file_name="audios_gerados.zip", mime="application/zip")

if st.button("🧹 Limpar Arquivos Temporários"):
    limpar_audios()
    st.session_state.arquivos = []
    st.success("Arquivos de áudio temporários foram removidos com sucesso!")