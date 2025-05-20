import threading
from vtuber_ai.core.config import load_config
from vtuber_ai.core.response_gen import generate_response
from vtuber_ai.utils.text import clean_text
from typing import List

class ConversationService:
    def __init__(self):
        self.config = load_config()
        self.conversation_memory: List[str] = []
        self.lock = threading.Lock()
        self.max_memory_length = self.config["MAX_MEMORY_LENGTH"]

    def add_user_message(self, message: str):
        with self.lock:
            self.conversation_memory.append(f"User: {message}")
            self.conversation_memory = self.conversation_memory[-self.max_memory_length:]

    def add_ai_message(self, message: str):
        with self.lock:
            self.conversation_memory.append(f"Airi: {message}")

    def build_prompt(self) -> str:
        with self.lock:
            prompt = self.config["VTUBER_PERSONALITY"] + "\n" + "\n".join(self.conversation_memory) + "\nAiri:"
        return prompt

    def get_response(self, user_message: str) -> str:
        self.add_user_message(user_message)
        prompt = self.build_prompt()
        response = generate_response(prompt, clean_text)
        self.add_ai_message(response)
        return response
