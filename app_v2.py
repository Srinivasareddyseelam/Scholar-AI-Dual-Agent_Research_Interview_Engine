#!/usr/bin/env python3
"""
Scholar AI - Research Paper Digest
A beautiful Streamlit interface powered by Ollama (FREE local LLM)
Using native Streamlit chat components for reliability
"""

import streamlit as st
import tempfile
import os
import time

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scholar AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── FONTS ── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── ROOT VARIABLES ── */
:root {
    --bg-deep:     #080c14;
    --bg-card:     #0e1523;
    --bg-panel:    #121929;
    --border:      #1e2d47;
    --accent-gold: #f0c060;
    --accent-teal: #29d9c2;
    --accent-rose: #ff6b8a;
    --accent-blue: #4a9eff;
    --text-primary: #e8edf5;
    --text-muted:   #6b82a0;
}

/* ── GLOBAL RESET ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
}

.main .block-container {
    padding: 1.5rem 2rem 3rem;
    max-width: 1400px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border);
}

/* ── TITLE AREA ── */
.scholar-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-teal) 60%, var(--accent-blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 0;
}
.scholar-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* ── STATUS PILLS ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.status-ready   { background: rgba(41,217,194,0.15); color: var(--accent-teal); border: 1px solid rgba(41,217,194,0.3); }
.status-loading { background: rgba(240,192,96,0.15);  color: var(--accent-gold); border: 1px solid rgba(240,192,96,0.3); }
.status-error   { background: rgba(255,107,138,0.15); color: var(--accent-rose); border: 1px solid rgba(255,107,138,0.3); }

/* ── STREAMLIT CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
}

[data-testid="stChatMessage"][data-testid*="user"] {
    background: linear-gradient(135deg, rgba(255,107,138,0.08) 0%, rgba(180,60,255,0.05) 100%) !important;
    border: 1px solid rgba(255,107,138,0.2) !important;
}

/* ── SOURCE CHIPS ── */
.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    background: rgba(74,158,255,0.15);
    border: 1px solid rgba(74,158,255,0.25);
    border-radius: 12px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--accent-blue);
    margin: 0.5rem 0.25rem 0 0;
}

/* ── INFO CARDS ── */
.info-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.info-card h4 {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 0.6rem 0;
}

/* ── STREAMLIT OVERRIDES ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-teal), var(--accent-blue)) !important;
    color: #000 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(41,217,194,0.3) !important;
}

div[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
    background: rgba(74,158,255,0.03) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

.brand-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}

/* Progress bar */
.progress-bar {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
defaults = {
    "chat_history": [],
    "vectorstore": None,
    "paper_summary": None,
    "journalist": None,
    "author": None,
    "topic": "",
    "exchange_count": 0,
    "max_exchanges": 10,
    "last_answer": "",
    "ready": False,
    "paper_name": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-bar">
    <div>
        <div class="scholar-title">Scholar AI</div>
        <div class="scholar-sub">⚛ Autonomous Research Interview Engine · Powered by Ollama</div>
    </div>
    <div style="text-align:right">
        <span class="status-pill status-ready">● LOCAL · FREE · PRIVATE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
        <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                    color:var(--accent-gold);margin-bottom:0.2rem">⚗ Scholar AI</div>
        <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                    color:var(--text-muted);letter-spacing:0.15em">RESEARCH INTERVIEW ENGINE</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    st.markdown("### 📄 Upload Paper")
    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help="Upload any research paper in PDF format",
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.markdown(f"""
        <div class="info-card">
            <h4>📎 Loaded File</h4>
            <p style="color:var(--accent-teal);font-weight:500">{uploaded_file.name}</p>
            <p style="font-size:0.78rem;color:var(--text-muted);margin-top:4px">
                {uploaded_file.size / 1024:.1f} KB
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### ⚙ Configuration")

    topic = st.text_input(
        "Research Topic",
        placeholder="e.g., quantum computing, LLMs...",
        value=st.session_state.topic,
    )

    paper_name = st.text_input(
        "Session Name",
        placeholder="e.g., attention_paper",
        value=st.session_state.paper_name if st.session_state.paper_name else "",
        help="Used for embedding cache storage"
    )

    arxiv_id = st.text_input(
        "arXiv ID (optional)",
        placeholder="e.g., 2303.08774",
        help="Fetches abstract from arXiv automatically"
    )

    max_ex = st.slider("Max Interview Exchanges", 3, 20, st.session_state.max_exchanges)
    st.session_state.max_exchanges = max_ex

    st.markdown("<hr>", unsafe_allow_html=True)

    init_btn = st.button("🚀 Launch Interview", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🗑 Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Status panel
    st.markdown("### 🟢 System Status")
    if st.session_state.ready:
        st.markdown('<span class="status-pill status-ready">● INTERVIEW READY</span>', unsafe_allow_html=True)
    elif uploaded_file:
        st.markdown('<span class="status-pill status-loading">◌ AWAITING LAUNCH</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill status-error">○ NO PAPER LOADED</span>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2rem;font-family:'Space Mono',monospace;
                font-size:0.62rem;color:var(--text-muted);line-height:1.8">
        Requires Ollama + llama3.2<br>
        Embeddings: all-MiniLM-L6-v2<br>
        Vector DB: FAISS<br>
        Cost: $0.00 / session
    </div>
    """, unsafe_allow_html=True)


# ─── INITIALIZATION ───────────────────────────────────────────────────────────
if init_btn and uploaded_file:
    if not topic.strip():
        st.error("Please enter a research topic before launching.")
    else:
        st.session_state.topic = topic.strip()
        st.session_state.paper_name = paper_name.strip() if paper_name.strip() else "scholar_session"
        st.session_state.chat_history = []
        st.session_state.exchange_count = 0
        st.session_state.ready = False

        try:
            from embedding_engine import Embedder
            from chatbot import JournalistBot, AuthorBot

            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            prog_bar = st.progress(0, text="⚙ Initializing embedding engine...")
            time.sleep(0.3)

            embedding = Embedder()
            prog_bar.progress(20, text="📄 Loading and chunking PDF...")

            embedding.load_n_process_document(tmp_path)
            prog_bar.progress(45, text="🔢 Creating vector embeddings...")

            store_path = st.session_state.paper_name
            vectorstore = embedding.create_vectorstore(store_path=store_path)
            st.session_state.vectorstore = vectorstore
            prog_bar.progress(65, text="🧠 Generating paper summary...")

            arxiv_arg = arxiv_id.strip() if arxiv_id.strip() else None
            summary = embedding.create_summary(arxiv_id=arxiv_arg)
            st.session_state.paper_summary = summary
            prog_bar.progress(80, text="🎙 Waking up Journalist AI...")

            journalist = JournalistBot()
            journalist.instruct(topic=st.session_state.topic, abstract=summary)
            st.session_state.journalist = journalist
            prog_bar.progress(90, text="🔬 Waking up Author AI...")

            author = AuthorBot(vectorstore=vectorstore)
            author.instruct(topic=st.session_state.topic)
            st.session_state.author = author
            prog_bar.progress(100, text="✅ Interview ready!")

            os.unlink(tmp_path)
            st.session_state.ready = True
            time.sleep(0.5)
            st.rerun()

        except ImportError as e:
            st.error(f"Missing dependency: {e}\n\nRun: `pip install -r requirements.txt`")
        except Exception as e:
            st.error(f"Initialization error: {str(e)}\n\nMake sure Ollama is running with llama3.2 installed.")

elif init_btn and not uploaded_file:
    st.warning("Please upload a PDF paper first.")


# ─── MAIN INTERVIEW UI ────────────────────────────────────────────────────────
if not st.session_state.ready:
    st.info("👆 Upload a PDF paper in the sidebar and click **Launch Interview** to begin.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>🎙 Journalist AI</h4>
            <p>An expert technical journalist who reads your paper's abstract and asks precise, 
            probing questions — guiding the conversation toward key insights and contributions.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>🔬 Author AI</h4>
            <p>The paper's author, powered by FAISS vector retrieval. Answers are grounded in 
            the actual paper content, cited by page number for full transparency.</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Show paper summary (always visible, no dropdown)
    if st.session_state.paper_summary:
        st.markdown("""
        <div class="info-card">
            <h4>📋 PAPER SUMMARY</h4>
        </div>
        """, unsafe_allow_html=True)
        st.write(st.session_state.paper_summary)  # Show full summary
        st.markdown("<hr>", unsafe_allow_html=True)

    # Progress bar
    n = st.session_state.exchange_count
    mx = st.session_state.max_exchanges
    st.markdown(f"""
    <div class="progress-bar">
        EXCHANGE {n}/{mx} · {mx - n} remaining
    </div>
    """, unsafe_allow_html=True)

    # Display chat history using native Streamlit chat
    for msg in st.session_state.chat_history:
        role = msg["role"]
        text = msg["text"]
        sources = msg.get("sources")
        
        if role == "journalist":
            with st.chat_message("assistant", avatar="🎙️"):
                st.markdown("**Journalist AI**")
                st.write(text)
        elif role == "author":
            with st.chat_message("assistant", avatar="🔬"):
                st.markdown("**Author AI**")
                st.write(text)
                if sources:
                    pages = list(set([str(s.metadata.get('page', '?') + 1) for s in sources]))
                    st.caption(f"📄 Sources: Pages {', '.join(pages)}")
        else:  # user
            with st.chat_message("user", avatar="👤"):
                st.write(text)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Action buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.session_state.exchange_count < st.session_state.max_exchanges:
            if st.button("▶ Next Exchange", use_container_width=True):
                try:
                    journalist = st.session_state.journalist
                    author = st.session_state.author

                    with st.spinner("🎙 Journalist is thinking..."):
                        if st.session_state.exchange_count == 0:
                            question = journalist.step("Start the interview with your first question about this paper.")
                        else:
                            question = journalist.step(st.session_state.last_answer)

                    st.session_state.chat_history.append({
                        "role": "journalist",
                        "text": question,
                    })

                    with st.spinner("🔬 Author is retrieving from paper..."):
                        answer, sources = author.step(question)

                    st.session_state.chat_history.append({
                        "role": "author",
                        "text": answer,
                        "sources": sources,
                    })

                    st.session_state.last_answer = answer
                    st.session_state.exchange_count += 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error during exchange: {e}")
        else:
            st.success("✦ Interview Complete — Maximum exchanges reached")

    # User question input
    st.markdown("---")
    st.markdown("💬 **Ask the Author Directly**")
    
    user_question = st.chat_input("Ask anything about the paper...")
    
    if user_question:
        try:
            author = st.session_state.author
            
            st.session_state.chat_history.append({
                "role": "user",
                "text": user_question,
            })

            with st.spinner("🔬 Author is searching the paper..."):
                answer, sources = author.step(user_question)

            st.session_state.chat_history.append({
                "role": "author",
                "text": answer,
                "sources": sources,
            })
            
            st.session_state.last_answer = answer
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")


# ─── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding:1.5rem;
            border-top:1px solid var(--border)">
    <span style="font-family:'Space Mono',monospace;font-size:0.65rem;
                  color:var(--text-muted);letter-spacing:0.12em">
        SCHOLAR AI · BUILT ON OLLAMA + LANGCHAIN + FAISS · 100% LOCAL · 100% FREE
    </span>
</div>
""", unsafe_allow_html=True)
