import streamlit as st
from pdf2docx import Converter
import tempfile
import os
import time

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="PDF → Word",
    page_icon="📄",
    layout="centered"
)

# ---------------------------
# CSS RETRO
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Courier+Prime:wght@400;700&display=swap');

html, body, [class*="css"] {
    background-color: #F5F0E8 !important;
    color: #2C2416 !important;
    font-family: 'IM Fell English', Georgia, serif !important;
}

/* Esconder elementos padrão do Streamlit */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 680px !important; }

/* Barra topo */
.top-bar {
    background: #2C3E50;
    height: 5px;
    margin: -2rem -2rem 2rem -2rem;
    border-radius: 0;
}

/* Título */
.retro-title {
    font-family: 'IM Fell English', Georgia, serif;
    font-size: 2.8rem;
    font-weight: bold;
    color: #2C3E50;
    letter-spacing: 0.05em;
    margin: 0;
    line-height: 1;
}

.retro-subtitle {
    font-family: 'IM Fell English', Georgia, serif;
    font-style: italic;
    font-size: 0.9rem;
    color: #8A7560;
    margin-top: 0.3rem;
    margin-bottom: 1.5rem;
}

.divider {
    border: none;
    border-top: 1px solid #C8B99A;
    margin: 1rem 0 1.5rem 0;
}

/* Cartão */
.retro-card {
    background: #FFFDF7;
    border: 1px solid #C8B99A;
    border-radius: 2px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
}

/* Upload zone */
[data-testid="stFileUploader"] {
    background: #FFFDF7 !important;
    border: 1.5px dashed #C8B99A !important;
    border-radius: 2px !important;
    padding: 1rem !important;
    font-family: 'Courier Prime', monospace !important;
}

[data-testid="stFileUploader"] label {
    font-family: 'IM Fell English', Georgia, serif !important;
    font-style: italic;
    color: #8A7560 !important;
    font-size: 0.9rem !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #8A7560 !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 0.85rem !important;
}

/* Botão principal */
.stButton > button {
    font-family: 'Courier Prime', monospace !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.08em;
    background: #FFFDF7 !important;
    color: #C0392B !important;
    border: 1.5px solid #C0392B !important;
    border-radius: 2px !important;
    padding: 0.6rem 2.5rem !important;
    transition: all 0.15s ease !important;
    width: 100%;
}

.stButton > button:hover {
    background: #C0392B !important;
    color: white !important;
}

/* Progress bar */
.stProgress > div > div {
    background-color: #2C3E50 !important;
}

/* Log terminal */
.log-box {
    background: #1A160F;
    color: #A8D5A2;
    font-family: 'Courier Prime', monospace;
    font-size: 0.8rem;
    padding: 1rem 1.2rem;
    border-radius: 2px;
    border: 1px solid #C8B99A;
    min-height: 140px;
    max-height: 220px;
    overflow-y: auto;
    line-height: 1.7;
    white-space: pre-wrap;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    font-family: 'Courier Prime', monospace !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    background: #FFFDF7 !important;
    color: #27AE60 !important;
    border: 1.5px solid #27AE60 !important;
    border-radius: 2px !important;
    width: 100% !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.15s ease !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: #27AE60 !important;
    color: white !important;
}

/* Rodapé */
.bottom-bar {
    background: #2C3E50;
    height: 5px;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
}

.log-label {
    font-family: 'IM Fell English', Georgia, serif;
    font-style: italic;
    font-size: 0.8rem;
    color: #8A7560;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# LAYOUT
# ---------------------------
st.markdown('<div class="top-bar"></div>', unsafe_allow_html=True)
st.markdown('<p style="font-family: \'IM Fell English\', Georgia, serif; font-size: 3rem; font-style: italic; color: #8A7560; margin-bottom: 0.1rem;">Fred\'s PDF to Word</p>', unsafe_allow_html=True)
st.markdown('<p class="retro-title">PDF → WORD</p>', unsafe_allow_html=True)
st.markdown('<p class="retro-subtitle">conversor de documentos &nbsp;·&nbsp; v1.0</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# -- Upload --
uploaded = st.file_uploader(
    "Ficheiro PDF de entrada",
    type=["pdf"],
    label_visibility="visible"
)

# -- Log state --
if "log_lines" not in st.session_state:
    st.session_state.log_lines = ["Pronto. Carrega um PDF para começar."]

if "docx_bytes" not in st.session_state:
    st.session_state.docx_bytes = None

if "output_name" not in st.session_state:
    st.session_state.output_name = "documento.docx"

# -- Botão converter --
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    converter_btn = st.button("[ CONVERTER ]")

# -- Conversão --
if converter_btn:
    if not uploaded:
        st.warning("Seleciona um ficheiro PDF primeiro.")
    else:
        st.session_state.docx_bytes = None
        st.session_state.log_lines = []

        def add_log(msg):
            ts = time.strftime("%H:%M:%S")
            st.session_state.log_lines.append(f"[{ts}]  {msg}")

        add_log("─" * 34)
        add_log("Conversão iniciada...")

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path  = os.path.join(tmpdir, "input.pdf")
            docx_path = os.path.join(tmpdir, "output.docx")

            with open(pdf_path, "wb") as f:
                f.write(uploaded.read())

            try:
                start = time.time()
                cv = Converter(pdf_path)
                total = len(cv.pages)
                add_log(f"Total de páginas: {total}")

                progress = st.progress(0, text="A processar...")

                for i in range(total):
                    add_log(f"A processar página {i+1} de {total}...")
                    progress.progress((i + 1) / total,
                                      text=f"Página {i+1} de {total}")

                cv.convert(docx_path, start=0, end=None)
                cv.close()

                progress.empty()

                with open(docx_path, "rb") as f:
                    st.session_state.docx_bytes = f.read()

                duration = round(time.time() - start, 2)
                st.session_state.output_name = uploaded.name.replace(".pdf", ".docx")
                add_log(f"Concluído em {duration}s")
                add_log("─" * 34)

            except Exception as e:
                add_log(f"ERRO: {e}")

# -- Download --
if st.session_state.docx_bytes:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="[ DESCARREGAR .DOCX ]",
            data=st.session_state.docx_bytes,
            file_name=st.session_state.output_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# -- Log --
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="log-label">registo de actividade</p>', unsafe_allow_html=True)
log_content = "\n".join(st.session_state.log_lines)
st.markdown(f'<div class="log-box">{log_content}</div>', unsafe_allow_html=True)

st.markdown('<div class="bottom-bar"></div>', unsafe_allow_html=True)