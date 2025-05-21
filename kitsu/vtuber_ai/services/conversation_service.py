import threading
import logging
from typing import Optional

from vtuber_ai.core.config_manager import Config
from vtuber_ai.core.response_gen import generate_response
from ai.text_utils import process_text_for_speech
from vtuber_ai.utils.text import clean_text
from lorebook.prompt_manager import build_full_prompt
from ai.memory_module import ConversationMemory

# Ensure logging is configured to show INFO and DEBUG messages in the terminal
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

AI_NAME = "Airi"

class ConversationService:
    def __init__(self, response_fn=generate_response):
        """
        Handles conversation state, memory, and response generation for the AI character.
        """
        self.lock = threading.Lock()
        self.memory = ConversationMemory()
        self.response_fn = response_fn

        self.max_memory_length = Config.max_memory_length()
        self.streamer_name = Config.streamer_name()
        self.vtuber_personality = build_full_prompt(self.streamer_name)

    def add_user_message(self, message: str) -> None:
        """
        Safely adds a user message to the memory.
        """
        with self.lock:
            self.memory.add_user(f"User: {message}")
            logging.debug(f"User message added to memory: {message}")

    def add_ai_message(self, message: str) -> None:
        """
        Safely adds an AI response to the memory.
        """
        with self.lock:
            self.memory.add_ai(f"{AI_NAME}: {message}")
            logging.debug(f"AI message added to memory: {message}")

    def build_prompt(self) -> str:
        """
        Builds the full prompt including personality, memory, and facts.
        """
        sections = [
            f"[PERSONALITY]\n{self.vtuber_personality.strip()}",
        ]

        if self.memory.summary:
            sections.append(f"[SUMMARY]\n{self.memory.summary.strip()}")

        if self.memory.facts:
            facts_section = "[KNOWN FACTS]\n" + "\n".join(
                f"- {k}: {v}" for k, v in self.memory.facts.items()
            )
            sections.append(facts_section)

        conversation_section = "[RECENT CONVERSATION]\n" + "\n".join(self.memory.memory)
        sections.append(conversation_section)

        full_prompt = "\n\n".join(sections) + f"\n\n{AI_NAME}:"
        logging.debug("Prompt built successfully.")
        return full_prompt

    def get_response(self, user_message: str) -> str:
        """
        Handles the full cycle of receiving a user message and generating an AI response.
        """
        try:
            logging.info(f'{AI_NAME} is thinking...')
            self.add_user_message(user_message)

            prompt = self.build_prompt()
            response = self.response_fn(prompt, process_text_for_speech)

            self.add_ai_message(response)
            return response

        except Exception as e:
            logging.exception(f"Error generating response: {e}")
            return "Sorry, something went wrong."

