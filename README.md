# 🔬 Scholar AI — Dual-Agent Research Interview Engine

> **An autonomous AI system that reads any research paper and conducts a full journalist-vs-author interview — entirely on your machine, for free.**

---

## ✦ What is Scholar AI?

Scholar AI is a **dual-agent research interview engine** built on top of Ollama, LangChain, and FAISS. Drop in any academic PDF, and two AI agents spring to life:

- 🎙 **Journalist AI** — A technically sharp reporter that reads the paper's abstract and fires probing, contextual questions — one at a time, building depth across up to 10 exchanges.
- 🔬 **Author AI** — The paper's simulated author, grounded via FAISS vector retrieval. Every answer is pulled directly from the paper's content and cited by page number.

The result: a structured, readable interview that distills a dense research paper into rich, accessible insight — no API key, no cloud calls, no cost.

---

## 🖥 Demo

```
Exchange 1/10
────────────────────────────────────────────────────────

🎙 Journalist AI
  "You mentioned your model outperforms the baseline by 14% on F1. Can you walk 
   us through what architectural decisions drove that improvement?"

🔬 Author AI
  "According to the paper, the key gain came from our novel attention-gating 
   mechanism introduced in Section 3.2. Unlike standard transformers that treat 
   all token interactions equally..."
  📄 Sources: Pages 4, 7, 11
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      app_v2.py                          │
│              Streamlit UI + Orchestration               │
└────────────────┬────────────────┬───────────────────────┘
                 │                │
    ┌────────────▼──────┐  ┌──────▼──────────────┐
    │   JournalistBot   │  │     AuthorBot        │
    │   (chatbot.py)    │  │   (chatbot.py)       │
    │                   │  │                      │
    │  Ollama llama3.2  │  │  Ollama llama3.2     │
    │  + abstract ctx   │  │  + FAISS retriever   │
    └───────────────────┘  └──────────┬───────────┘
                                      │
                         ┌────────────▼────────────┐
                         │    embedding_engine.py   │
                         │                          │
                         │  HuggingFace Embeddings  │
                         │  all-MiniLM-L6-v2 (CPU)  │
                         │  FAISS Vector Store      │
                         │  PyMuPDF PDF Loader      │
                         └──────────────────────────┘
```

### Core Components

| File | Role |
|------|------|
| `app_v2.py` | Streamlit UI, session management, agent orchestration |
| `chatbot.py` | `JournalistBot` and `AuthorBot` agent classes |
| `embedding_engine.py` | PDF ingestion, chunking, FAISS indexing, summarization |

---

## ⚙ How It Works

1. **Upload a PDF** — any research paper, preprint, or report.
2. **Set a topic & optional arXiv ID** — used to focus the journalist's angle and optionally fetch the abstract directly from arXiv.
3. **Launch Interview** — the engine:
   - Loads and chunks the PDF (`RecursiveCharacterTextSplitter`, 1000 tokens / 100 overlap)
   - Builds a FAISS vector store using `sentence-transformers/all-MiniLM-L6-v2`
   - Generates a paper summary (via Ollama or arXiv metadata)
   - Boots both AI agents
4. **Step through exchanges** — click **▶ Next Exchange** to advance the dialogue. The Journalist reads the last Author answer and asks the next question; the Author retrieves the top-5 relevant paper chunks and responds.
5. **Ask your own questions** — use the chat input at the bottom to query the Author directly at any point.

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.9+**
- **[Ollama](https://ollama.com)** installed and running locally
- `llama3.2` model pulled in Ollama

```bash
# Install and start Ollama
ollama pull llama3.2
ollama serve
```

### 2. Clone & Install

```bash
git clone https://github.com/your-username/scholar-ai.git
cd scholar-ai
pip install -r requirements.txt
```

### 3. Run

```bash
streamlit run app_v2.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📦 Requirements

```txt
streamlit
langchain
langchain-ollama
langchain-community
langchain-text-splitters
faiss-cpu
sentence-transformers
pymupdf
arxiv
```

Install all at once:

```bash
pip install streamlit langchain langchain-ollama langchain-community \
            langchain-text-splitters faiss-cpu sentence-transformers \
            pymupdf arxiv
```

---

## 🧩 Project Structure

```
scholar-ai/
├── app_v2.py              # Main Streamlit app
├── chatbot.py             # JournalistBot + AuthorBot agents
├── embedding_engine.py    # PDF processing + FAISS + summarization
├── requirements.txt
└── README.md
```

---

## ✨ Features

- **Zero cost** — runs fully on your hardware via Ollama; no OpenAI or Anthropic API key needed
- **100% private** — no data leaves your machine
- **Autonomous interview flow** — up to 10 journalist-author exchanges, each building on the last
- **RAG-grounded answers** — Author AI cites page numbers drawn from FAISS retrieval
- **arXiv integration** — paste an arXiv ID to auto-fetch a polished abstract as the summary
- **Persistent vector store** — embeddings are saved to disk; re-opening the same paper skips re-embedding
- **Direct Q&A mode** — ask the Author anything outside the automated interview flow
- **Beautiful dark UI** — Streamlit interface styled with Playfair Display + Space Mono

---

## 🎛 Configuration

All key settings are accessible from the sidebar UI:

| Setting | Default | Description |
|---------|---------|-------------|
| Research Topic | *(required)* | Focuses both agents on a specific angle |
| Paper Name / Session ID | `scholar_session` | Used as the FAISS store directory name |
| arXiv ID | *(optional)* | Fetches abstract metadata instead of LLM summarization |
| Max Exchanges | `10` | Number of journalist-author turns |

To change model or chunk sizes, edit the relevant constants in `chatbot.py` and `embedding_engine.py`.

---

## 🛠 Customisation

**Swap the LLM model** — edit `chatbot.py`:
```python
self.llm = ChatOllama(model="mistral", temperature=0.7)
```

**Change retrieval depth** — edit `chatbot.py` in `AuthorBot.__init__`:
```python
self.retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
```

**Use GPU embeddings** — edit `embedding_engine.py`:
```python
model_kwargs={"device": "cuda"}
```

---
