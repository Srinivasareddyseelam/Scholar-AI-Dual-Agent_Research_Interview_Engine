# Content: Chatbot implementation using Ollama (FREE local LLM)
# Author: Modified for Ollama implementation
# Date: February, 2026
# Cost: $0 - Runs entirely on your computer
# Updated: Migrated to langchain-ollama (non-deprecated)

from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama


class Chatbot(ABC):
    """Base chatbot class using Ollama."""

    def __init__(self):
        self.llm = ChatOllama(
            model="llama3.2",
            temperature=0.7,
            num_predict=1024,  # Allow longer responses (default is ~128)
        )

    @abstractmethod
    def instruct(self, *args, **kwargs):
        pass

    @abstractmethod
    def step(self, prompt):
        pass

    @abstractmethod
    def _specify_system_message(self):
        pass


# ===============================
# Journalist Bot
# ===============================

class JournalistBot(Chatbot):
    """Journalist bot using Ollama."""

    def __init__(self):
        super().__init__()
        self.chat_history = []

    def instruct(self, topic, abstract):
        self.topic = topic
        self.abstract = abstract

    def step(self, prompt):
        history_text = "\n".join(
            [f"Journalist: {q}\nAuthor: {a}" for q, a in self.chat_history]
        )

        full_prompt = f"""
{self._specify_system_message()}

Conversation so far:
{history_text}

Journalist question:
{prompt}
"""

        response = self.llm.invoke(full_prompt)
        answer = response.content

        self.chat_history.append((prompt, answer))
        return answer

    def _specify_system_message(self):
        return f"""
You are a technical journalist specializing in {self.topic}.
Your task is to interview the author of a scientific paper.

Guidelines:
- Ask one detailed, probing question at a time.
- Focus exclusively on the paper's content, methods, and findings.
- Ask questions that elicit comprehensive explanations (not yes/no questions).
- Build upon previous answers to go deeper into the research.
- Avoid general questions about the topic - stay focused on THIS paper.
- Lead the conversation toward understanding the key contributions and implications.
- Do not add labels like "Question:" or "Journalist:".
- Ask questions that would help readers understand the research thoroughly.

Abstract:
{self.abstract}
"""


# ===============================
# Author Bot
# ===============================

class AuthorBot(Chatbot):
    """Author bot using Ollama + FAISS retriever."""

    def __init__(self, vectorstore, debug=False):
        super().__init__()
        self.vectorstore = vectorstore
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # Increased from 3 to 5
        self.chat_history = []
        self.debug = debug

    def instruct(self, topic):
        self.topic = topic

    def step(self, prompt):
        # Retrieve relevant paper chunks
        docs = self.retriever.invoke(prompt)
        context = "\n\n".join([doc.page_content for doc in docs])

        history_text = "\n".join(
            [f"Journalist: {q}\nAuthor: {a}" for q, a in self.chat_history]
        )

        full_prompt = f"""
{self._specify_system_message()}

Conversation so far:
{history_text}

Relevant paper context:
{context}

Journalist question:
{prompt}
"""

        response = self.llm.invoke(full_prompt)
        answer = response.content

        self.chat_history.append((prompt, answer))

        return answer, docs

    def _specify_system_message(self):
        return f"""
You are the author of a scientific paper on {self.topic}.

You are being interviewed by a journalist about your research.

Guidelines:
- Provide detailed, comprehensive answers (3-5 paragraphs when appropriate).
- Answer clearly and technically, as an expert would.
- Use the provided paper context as your primary source.
- When citing the paper, say "According to the paper..." or "Our research shows...".
- When adding context beyond the paper, say "Based on general knowledge in the field...".
- Explain technical concepts thoroughly - assume the journalist wants depth.
- Use specific examples, data, or results from the paper when available.
- Break down complex ideas into understandable explanations.
- Do not prefix your response with labels like "Answer:" or "Response:".
- Provide enough detail to give a complete picture of the research.
"""
