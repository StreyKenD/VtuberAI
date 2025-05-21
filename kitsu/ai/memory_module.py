import json
import threading
from collections import deque
from pathlib import Path
from typing import Callable, Dict, Optional
import logging

class ConversationMemory:
    def __init__(
        self,
        max_len: int = 6,
        save_path: str = "data/conversation_memory.json",
        ai_name: str = "Airi"
    ):
        self.memory = deque(maxlen=max_len)
        self.lock = threading.RLock()
        self.summary: str = ""
        self.facts: Dict[str, str] = {}
        self.save_path = Path(save_path)
        self.ai_name = ai_name
        self.load()

    def save(self) -> None:
        """
        Thread-safe saving of memory to disk.
        """
        with self.lock:
            data = {
                "memory": list(self.memory),
                "summary": self.summary,
                "facts": self.facts
            }
            try:
                self.save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logging.debug(f"Conversation memory saved to {self.save_path}")
            except Exception as e:
                logging.exception(f"Failed to save conversation memory: {e}")

    def load(self) -> None:
        """
        Thread-safe loading of memory from disk.
        """
        if not self.save_path.exists():
            return
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            with self.lock:
                self.memory = deque(data.get("memory", []), maxlen=self.memory.maxlen)
                self.summary = data.get("summary", "")
                self.facts = data.get("facts", {})
            logging.debug("Conversation memory loaded.")
        except Exception as e:
            logging.warning(f"Failed to load conversation memory: {e}")

    def add_user(self, text: str) -> None:
        with self.lock:
            self.memory.append(f"User: {text}")
            self.save()

    def add_ai(self, text: str) -> None:
        with self.lock:
            self.memory.append(f"{self.ai_name}: {text}")
            self.save()

    def add_fact(self, key: str, value: str) -> None:
        with self.lock:
            self.facts[key] = value
            self.save()

    def update_summary(self, summarization_func: Callable[[str], str]) -> None:
        with self.lock:
            text_to_summarize = "\n".join(self.memory)
            self.summary = summarization_func(text_to_summarize)
            self.save()

    def clear(self) -> None:
        with self.lock:
            self.memory.clear()
            self.summary = ""
            self.facts.clear()
            self.save()
            logging.info("Conversation memory cleared.")

    def get_prompt_context(self, personality_prompt: str = "") -> str:
        """
        Returns the full prompt context used for LLM input.
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
