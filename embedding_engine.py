# Content: Embedding engine using HuggingFace (FREE local embeddings)
# Author: Modified for Ollama project
# Date: February, 2026
# Cost: $0 - Runs entirely on your computer

import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import ArxivAPIWrapper


class Embedder:
    """FREE Embedding engine using HuggingFace."""

    def __init__(self):
        """Initialize HuggingFace embeddings (runs locally, no API needed)."""

        print("Initializing embeddings model (first run may download ~90MB)...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        print("✓ Embeddings model ready!")

        self.documents = None
        self.vectorstore = None

    def load_n_process_document(self, path):
        """Load and process PDF document."""

        print(f"Loading PDF from: {path}")

        loader = PyMuPDFLoader(path)
        documents = loader.load()

        print(f"✓ Loaded {len(documents)} pages")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
        )

        self.documents = text_splitter.split_documents(documents)

        print(f"✓ Split into {len(self.documents)} chunks")

    def create_vectorstore(self, store_path):
        """Create or load FAISS vector store."""

        if self.documents is None:
            raise ValueError("No documents loaded. Run load_n_process_document() first.")

        if not os.path.exists(store_path):
            print("Creating embeddings... (this may take 1-2 minutes)")

            self.vectorstore = FAISS.from_documents(
                self.documents,
                self.embeddings,
            )

            self.vectorstore.save_local(store_path)

            print(f"✓ Embeddings saved to: {store_path}")

        else:
            print(f"Loading existing embeddings from: {store_path}")

            self.vectorstore = FAISS.load_local(
                store_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )

            print("✓ Embeddings loaded!")

        return self.vectorstore

    def create_summary(self, arxiv_id=None):
        """Create paper summary using Ollama or arXiv metadata."""

        if arxiv_id is None:
            if self.documents is None:
                raise ValueError("No documents loaded. Run load_n_process_document() first.")

            print("Generating summary with Ollama...")

            llm = ChatOllama(
                model="llama3.2",
                temperature=0.7,
            )

            # Combine first few chunks into a single prompt
            text_content = "\n\n".join(
                [doc.page_content for doc in self.documents[:3]]
            )

            prompt = f"""
            Summarize the following research paper clearly and concisely:

            {text_content}
            """

            response = llm.invoke(prompt)
            summary = response.content

            print("✓ Summary generated!")

        else:
            print(f"Fetching summary from arXiv: {arxiv_id}")

            arxiv = ArxivAPIWrapper()
            summary = arxiv.run(arxiv_id)

            summary = summary.replace("{", "(").replace("}", ")")

            print("✓ Summary fetched from arXiv!")

        return summary
