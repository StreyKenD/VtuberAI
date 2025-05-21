import threading
from vtuber_ai.core.config_manager import Config
from vtuber_ai.core.response_gen import generate_response
from kitsu.ai.text_utils import process_text_for_speech
from vtuber_ai.utils.text import clean_text
from typing import List
from lorebook.prompt_manager import build_full_prompt
from ai.memory_module import ConversationMemory
import logging

class ConversationService:
    def __init__(self):
        self.memory = ConversationMemory()
        self.lock = threading.Lock()
        self.max_memory_length = Config.max_memory_length()
        self.streamer_name = Config.streamer_name()
        self.vtuber_personality = build_full_prompt(self.streamer_name)

    def add_user_message(self, message: str):
        with self.lock:
            self.memory.add_user(f"User: {message}")
            self.conversation_memory = self.conversation_memory[-self.max_memory_length:]

    def add_ai_message(self, message: str):
        with self.lock:
            self.memory.add_ai(f"Airi: {message}")

    def build_prompt(self) -> str:
        prompt = "[PERSONALITY]\n" + self.vtuber_personality.strip() + "\n\n"

        if self.memory.summary:
            prompt += "[SUMMARY]\n" + self.memory.summary.strip() + "\n\n"

        if self.memory.facts:
            prompt += "[KNOWN FACTS]\n"
            for k, v in self.memory.facts.items():
                prompt += f"- {k}: {v}\n"
            prompt += "\n"

        prompt += "[RECENT CONVERSATION]\n" + "\n".join(self.memory.memory)
        prompt += "\n\nAiri:"
        return prompt

    def get_response(self, user_message: str) -> str:
        logging.info('Airi is thinking...')
        self.add_user_message(user_message)
        prompt = self.build_prompt()
        response = generate_response(prompt, process_text_for_speech)
        self.add_ai_message(response)
        return response
