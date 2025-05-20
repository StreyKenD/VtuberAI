from collections import deque
import threading

class ConversationMemory:
    def __init__(self, max_len=6):
        self.memory = deque(maxlen=max_len)  # recent conversation
        self.lock = threading.Lock()
        self.summary = ""  # short summary string
        self.facts = {}    # dict of learned facts

    def add_user(self, text: str):
        with self.lock:
            self.memory.append(f"User: {text}")

    def add_ai(self, text: str):
        with self.lock:
            self.memory.append(f"Airi: {text}")

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

    def update_summary(self, summarization_func):
        """
        Use an LLM or your summarization function to generate a new summary
        based on conversation memory.
        """
        with self.lock:
            # Example: summarization_func takes a string and returns a summary string
            text_to_summarize = "\n".join(self.memory)
            self.summary = summarization_func(text_to_summarize)

    def add_fact(self, key: str, value: str):
        with self.lock:
            self.facts[key] = value
