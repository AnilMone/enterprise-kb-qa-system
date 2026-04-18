import os
import tempfile
import pathlib
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

_ENV_PATH = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun

st.set_page_config(
    page_title="Enterprise Knowledge Base Q&A System Using Amazon Bedrock Knowledge Bases",
    page_icon="K",
    layout="wide",
    initial_sidebar_state="expanded",
)

from bedrock_rag import query_knowledge_base, upload_document_to_s3
from config import APP_TITLE


def format_document_title(file_path: str) -> str:
    file_name = pathlib.Path(file_path).stem
    title = file_name.replace("_", " ").replace("-", " ")
    return " ".join(word.capitalize() for word in title.split())


def get_local_documents() -> list:
    root = pathlib.Path(__file__).parent / "docs"
    documents = []
    if root.exists():
        for dirpath, _, filenames in os.walk(root):
            for filename in sorted(filenames):
                if filename.lower().endswith((".pdf", ".txt", ".docx")):
                    documents.append(format_document_title(filename))
    return documents


def format_history(history):
    return [f"{item['timestamp']} - {item['question']}" for item in history]


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, .stApp {
      background: #fff3e0 !important;
      font-family: 'Inter', sans-serif !important;
      color: #1f2937 !important;
    }

    header[data-testid="stHeader"], #MainMenu, footer {
      display: none !important;
    }

    section[data-testid="stSidebar"] {
      background: #ffefde !important;
      border-right: 1px solid #f3d1a1 !important;
    }

    section[data-testid="stSidebar"] > div {
      padding: 2rem 1.2rem !important;
    }

    .main .block-container {
      padding: 2rem 2rem 3rem !important;
      max-width: 1400px !important;
      margin-left: auto !important;
      margin-right: auto !important;
    }

    .content-wrapper {
      max-width: 980px;
      margin-left: auto;
      margin-right: auto;
    }

    .brand-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 2rem;
    }

    .brand-icon {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: #d97706;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      color: #ffffff;
      font-weight: 700;
    }

    .brand-name {
      font-size: 1rem;
      font-weight: 800;
      color: #1f2937;
    }

    .nav-item {
      display: block;
      padding: 0.8rem 0.95rem;
      border-radius: 14px;
      font-size: 0.95rem;
      font-weight: 600;
      color: #475569;
      margin-bottom: 0.5rem;
      transition: all 0.2s ease;
      text-decoration: none;
    }

    .nav-item:hover {
      background: #fee2b3;
      color: #1f2937;
    }

    .nav-item.active {
      background: #d97706;
      color: #ffffff;
    }

    .section-label {
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #7c3aed;
      margin: 1.75rem 0 0.75rem;
    }

    .page-title {
      font-size: 2.4rem;
      font-weight: 800;
      color: #1f2937;
      margin-bottom: 0.35rem;
      text-align: center;
    }

    .page-subtitle {
      font-size: 1rem;
      color: #4b5563;
      line-height: 1.6;
      margin-bottom: 1.75rem;
      max-width: 820px;
      margin-left: auto;
      margin-right: auto;
      text-align: center;
    }

    .search-container {
      background: #ffffff;
      border: 1px solid #f3d1a1;
      border-radius: 24px;
      padding: 1.1rem 1.2rem;
      box-shadow: 0 18px 40px rgba(249, 115, 22, 0.08);
      margin: 0 auto 1.75rem;
      max-width: 840px;
    }
      background: #ffffff;
      border: 1px solid #f3d1a1;
      border-radius: 24px;
      padding: 1.1rem 1.2rem;
      box-shadow: 0 18px 40px rgba(249, 115, 22, 0.08);
      margin-bottom: 1.75rem;
    }

    .search-container .stTextInput>div>div>input {
      background: #fff7ed !important;
      border-radius: 16px !important;
      border: 1px solid #fcd9b6 !important;
      padding: 1rem 1.1rem !important;
      color: #1f2937 !important;
      font-size: 1rem !important;
      height: 3.2rem !important;
    }

    .search-container .stButton>button {
      width: 100% !important;
      background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%) !important;
      color: #ffffff !important;
      border: none !important;
      border-radius: 16px !important;
      font-size: 1rem !important;
      font-weight: 700 !important;
      padding: 0.9rem 1rem !important;
      margin-top: 0.75rem !important;
      box-shadow: 0 10px 25px rgba(249, 115, 22, 0.18) !important;
    }

    .card {
      background: #ffffff;
      border: 1px solid #f3d1a1;
      border-radius: 24px;
      padding: 1.5rem 1.75rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 18px 40px rgba(249, 115, 22, 0.06);
    }

    .msg-user, .msg-assistant {
      border-radius: 24px;
      padding: 1.2rem 1.4rem;
      margin-bottom: 1rem;
      line-height: 1.6;
    }

    .msg-user {
      background: #fff7ed;
      border: 1px solid #fcd9b6;
      color: #1f2937;
    }

    .msg-assistant {
      background: #ffffff;
      border: 1px solid #f3d1a1;
      color: #1f2937;
    }

    .msg-label {
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #9a3412;
      margin-bottom: 0.6rem;
    }

    .info-box {
      background: #fff7ed;
      border: 1px solid #fcd9b6;
      border-radius: 18px;
      padding: 1rem 1.2rem;
      color: #92400e;
      margin-bottom: 1.2rem;
    }

    .doc-card {
      background: #fffbf3;
      border: 1px solid #f7d9aa;
      border-radius: 18px;
      padding: 1rem 1.1rem;
      margin-bottom: 1rem;
    }

    .doc-title {
      font-size: 0.98rem;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 0.55rem;
    }

    .doc-text {
      font-size: 0.9rem;
      color: #475569;
      line-height: 1.5;
      margin-bottom: 0.8rem;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
      background: #fde7c7;
      color: #92400e;
      font-size: 0.8rem;
      font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

if "nav" not in st.session_state:
    st.session_state.nav = "Knowledge Bases"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_citations" not in st.session_state:
    st.session_state.current_citations = []
if "question_history" not in st.session_state:
    st.session_state.question_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
          <div class="brand-icon">K</div>
          <span class="brand-name">Enterprise KB Q&A</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = st.radio(
        label="",
        options=["Knowledge Bases", "Documents", "Analytics", "Settings"],
        index=["Knowledge Bases", "Documents", "Analytics", "Settings"].index(st.session_state.nav),
        label_visibility="collapsed",
    )
    st.session_state.nav = selected

    st.markdown("<div class='section-label'>Upload Documents</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.82rem; color:#6b7280; margin:0 0 0.8rem;'>Upload PDF, TXT, or DOCX files into the knowledge base.</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"], label_visibility="collapsed")
    if uploaded_file is not None:
        with st.spinner(f"Uploading {uploaded_file.name}..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_path = os.path.join(tmpdir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                success = upload_document_to_s3(temp_path, uploaded_file.name)
        if success:
            st.success("Uploaded successfully!")
            st.session_state.uploaded_files.append(format_document_title(uploaded_file.name))
        else:
            st.error("Upload failed. Check your AWS credentials or S3 permissions.")

    st.markdown("<div class='section-label'>Local Documents</div>", unsafe_allow_html=True)
    local_docs = get_local_documents()
    st.markdown(f"<div style='font-size:0.9rem; color:#475569; margin-bottom:0.4rem;'>Files found: {len(local_docs)}</div>", unsafe_allow_html=True)
    for item in local_docs[:6]:
        st.markdown(f"<div style='font-size:0.9rem; color:#1f2937; margin-bottom:0.35rem;'>- {item}</div>", unsafe_allow_html=True)
    if len(local_docs) > 6:
        st.markdown(f"<div style='font-size:0.85rem; color:#6b7280;'>and {len(local_docs) - 6} more...</div>", unsafe_allow_html=True)

st.markdown(f"<div class='page-title'>Enterprise Knowledge Base Q&A System</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='page-subtitle'>Use Amazon Bedrock Knowledge Bases to search your documents, visualize recent question activity, and manage your Q&A history.</div>",
    unsafe_allow_html=True,
)

if st.session_state.nav == "Knowledge Bases":
    with st.form("search_form", clear_on_submit=False):
        st.markdown("<div class='search-container'>", unsafe_allow_html=True)
        question_input = st.text_input("Ask Your Query", placeholder="Ask Your Query", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        search_btn = st.form_submit_button("Search")

    if search_btn and question_input and question_input.strip():
        question = question_input.strip()
        st.session_state.messages.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        st.session_state.question_history.append({
            "question": question,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

        with st.spinner("Searching knowledge base..."):
            result = query_knowledge_base(question)

        if result["success"]:
            st.session_state.current_citations = result.get("citations", [])
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
        else:
            st.error(result["answer"])

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="msg-user"><div class="msg-label">Your question</div>{message["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-assistant"><div class="msg-label">AI response</div>{message["content"]}</div>',
                unsafe_allow_html=True,
            )

    if st.session_state.current_citations:
        with st.expander(f"Sources referenced: {len(st.session_state.current_citations)}"):
            for i, citation in enumerate(st.session_state.current_citations, 1):
                source_file = citation["source"].split("/")[-1]
                display_name = format_document_title(source_file)
                st.markdown(f"<div class='doc-card'><div class='doc-title'>Source {i}: {display_name}</div><div class='doc-text'>{citation['excerpt']}</div></div>", unsafe_allow_html=True)

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_citations = []
        st.rerun()

elif st.session_state.nav == "Documents":
    st.markdown("<div class='card'><div class='doc-title'>Document Library</div><div class='doc-text'>Browse the documents available in the local docs folder and newly uploaded files.</div></div>", unsafe_allow_html=True)
    all_docs = list(local_docs)
    all_docs.extend(st.session_state.uploaded_files)

    if all_docs:
        for idx, doc in enumerate(sorted(set(all_docs)), 1):
            st.markdown(
                f"<div class='doc-card'><div class='doc-title'>{idx}. {doc}</div><div class='doc-text'>Stored in the knowledge base and available for retrieval.</div></div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No documents are available yet. Upload files from the sidebar or add docs to the docs folder.")

elif st.session_state.nav == "Analytics":
    st.markdown("<div class='card'><div class='doc-title'>Question Analytics</div><div class='doc-text'>Visualize how many queries have been asked during this session.</div></div>", unsafe_allow_html=True)

    if st.session_state.question_history:
        counts = [i + 1 for i in range(len(st.session_state.question_history))]
        st.line_chart(counts)

        st.markdown("<div class='doc-title'>Recent Questions</div>", unsafe_allow_html=True)
        for item in reversed(st.session_state.question_history[-6:]):
            st.markdown(f"<div class='doc-card'><div class='doc-text'>{item['timestamp']}: {item['question']}</div></div>", unsafe_allow_html=True)
    else:
        st.info("Ask questions in the Knowledge Bases section to populate analytics.")

elif st.session_state.nav == "Settings":
    st.markdown("<div class='card'><div class='doc-title'>Question History</div><div class='doc-text'>Review your recent queries and clear the stored history if needed.</div></div>", unsafe_allow_html=True)

    if st.session_state.question_history:
        for entry in reversed(st.session_state.question_history[-10:]):
            st.markdown(f"<div class='doc-card'><div class='doc-text'>{entry['timestamp']} - {entry['question']}</div></div>", unsafe_allow_html=True)

        if st.button("Clear History", use_container_width=True):
            st.session_state.question_history = []
            st.session_state.messages = []
            st.session_state.current_citations = []
            st.rerun()
    else:
        st.info("No question history is available yet.")

    st.markdown("<div class='section-label'>Application Info</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='info-box'>This app uses Amazon Bedrock Knowledge Bases for retrieval-augmented generation of answers from document content.</div>",
        unsafe_allow_html=True,
    )
