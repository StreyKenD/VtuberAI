import json
import threading
from collections import deque
from pathlib import Path
from typing import Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# LangChain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_community.chat_models import ChatOllama

class ConversationMemory:
    def __init__(
        self,
        max_len: int = 6,
        save_path: str = "data/facts.json",
        ai_name: str = "Kitsu.exe"
    ):
        self.memory = deque(maxlen=max_len)
        self.lock = threading.RLock()
        self.summary: str = ""
        self.facts: Dict[str, str] = {}
        self.save_path = Path(save_path)
        self.ai_name = ai_name
        self.load_facts()

    def add_user(self, text: str) -> None:
        with self.lock:
            self.memory.append(f"User: {text}")

    def add_ai(self, text: str) -> None:
        with self.lock:
            self.memory.append(f"{self.ai_name}: {text}")

    def set_summary(self, summary: str) -> None:
        """Sets a new summary (called after extracting <summary> from LLM)."""
        with self.lock:
            self.summary = summary.strip()

    def add_fact(self, key: str, value: str) -> None:
        with self.lock:
            self.facts[key] = value

    def clear(self) -> None:
        with self.lock:
            self.memory.clear()
            self.summary = ""
            self.facts.clear()
            logger.info("Conversation memory cleared.")

    def get_prompt_context(self, personality_prompt: str = "") -> str:
        """
        Returns the full prompt context used for LLM input.
        Includes personality, summary, known facts, and recent memory.
        """
        with self.lock:
            parts = []

            if personality_prompt:
                parts.append(f"[PERSONALITY]\n{personality_prompt.strip()}")

            if self.summary:
                parts.append(f"[SUMMARY]\n{self.summary.strip()}")

            if self.facts:
                fact_lines = "\n".join(f"{k}: {v}" for k, v in self.facts.items())
                parts.append(f"[FACTS]\n{fact_lines}")

            if self.memory:
                memory_lines = "\n".join(self.memory)
                parts.append(f"[RECENT CONVERSATION]\n{memory_lines}")

            return "\n\n".join(parts)

    def save_facts(self) -> None:
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(self.facts, f, indent=2, ensure_ascii=False)
            logger.debug(f"Facts saved to {self.save_path}")
        except Exception as e:
            logger.error(f"Failed to save facts: {e}")

    def load_facts(self) -> None:
        if not self.save_path.exists():
            return
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                self.facts = json.load(f)
            logger.debug(f"Facts loaded from {self.save_path}")
        except Exception as e:
            logger.warning(f"Failed to load facts: {e}")

    def summarize_with_langchain(self, llm=None) -> str:
        """Summarizes recent memory using LangChain + Ollama Mistral."""
        with self.lock:
            if not self.memory:
                return ""

            if llm is None:
                llm = ChatOllama(model="mistral", temperature=0.3)

            prompt_template = PromptTemplate.from_template(
                "Summarize the following conversation between User and {ai_name}:\n\n{chat}\n\nSummary:"
            )

            chain: Runnable = prompt_template | llm | StrOutputParser()
            recent_chat = "\n".join(self.memory)
            summary = chain.invoke({"chat": recent_chat, "ai_name": self.ai_name})
            self.set_summary(summary)
            return summary