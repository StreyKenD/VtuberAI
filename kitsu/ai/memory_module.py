from collections import deque
import threading
from pathlib import Path
import json

class ConversationMemory:
    def __init__(self, max_len=6, save_path="data/conversation_memory.json"):
        self.memory = deque(maxlen=max_len)
        self.lock = threading.Lock()
        self.summary = ""
        self.facts = {}
        self.save_path = Path(save_path)
        self.load()

    def save(self):
        with self.lock:
            data = {
                "memory": list(self.memory),
                "summary": self.summary,
                "facts": self.facts
            }
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self):
        if self.save_path.exists():
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                with self.lock:
                    self.memory = deque(data.get("memory", []), maxlen=self.memory.maxlen)
                    self.summary = data.get("summary", "")
                    self.facts = data.get("facts", {})

    def add_user(self, text: str):
        with self.lock:
            self.memory.append(f"User: {text}")
            self.save()

    def add_ai(self, text: str):
        with self.lock:
            self.memory.append(f"Airi: {text}")
            self.save()

    def get_prompt_context(self, personality_prompt: str = "") -> str:
        with self.lock:
            prompt = "[PERSONALITY]\n" + personality_prompt + "\n\n"
            prompt += "[SUMMARY]\n" + self.summary + "\n\n"
            prompt += "[FACTS]\n"
            for k, v in self.facts.items():
                prompt += f"{k}: {v}\n"
            prompt += "\n[RECENT CONVERSATION]\n" + "\n".join(self.memory)
            return prompt

    def clear(self):
        with self.lock:
            self.memory.clear()
            self.summary = ""
            self.facts.clear()
            self.save()

    def update_summary(self, summarization_func):
        with self.lock:
            text_to_summarize = "\n".join(self.memory)
            self.summary = summarization_func(text_to_summarize)
            self.save()

    def add_fact(self, key: str, value: str):
        with self.lock:
            self.facts[key] = value
            self.save()
