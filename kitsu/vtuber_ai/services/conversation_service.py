import threading
import logging
from typing import Optional

from vtuber_ai.core.config_manager import Config
from vtuber_ai.core.response_gen import generate_response
from ai.text_utils import process_text_for_speech
from vtuber_ai.utils.text import clean_text
from lorebook.prompt_manager import build_full_prompt, load_lorebook, PREDEFINED_KEYWORDS, get_lore_injections, LOREBOOK
from ai.memory_module import ConversationMemory

logger = logging.getLogger(__name__)

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

        # Load the lorebook at startup
        load_lorebook()
        self.keywords = PREDEFINED_KEYWORDS  # Initialize keywords from the lorebook

    def add_user_message(self, message: str) -> None:
        """
        Safely adds a user message to the memory.
        """
        with self.lock:
            self.memory.add_user(f"User: {message}")
            logger.debug(f"User message added to memory: {message}")

    def add_ai_message(self, message: str) -> None:
        """
        Safely adds an AI response to the memory.
        """
        with self.lock:
            self.memory.add_ai(f"{AI_NAME}: {message}")
            logger.debug(f"AI message added to memory: {message}")

    def extract_triggers(self, message: str) -> list[str]:
        """
        Extract triggers from the user message based on the lorebook.
        """
        triggers = []
        for entry in LOREBOOK:
            if entry["trigger"].lower() in message.lower():
                triggers.append(entry["trigger"])
        logger.debug(f"Extracted triggers from message '{message}': {triggers}")
        return triggers

    def build_prompt(self, user_message: str) -> str:
        """
        Builds the full prompt including personality, memory, facts, and lore.
        """
        # Extract triggers from the user message
        triggers = self.extract_triggers(user_message)

        # Get lore injections for "before_history" and "before_prompt" positions
        before_history_lore = get_lore_injections(triggers, "before_history")
        before_prompt_lore = get_lore_injections(triggers, "before_prompt")

        sections = []

        # Add lore before history
        if before_history_lore:
            sections.append(f"[LORE BEFORE HISTORY]\n" + "\n".join(before_history_lore))

        if hasattr(self.memory, "summary") and self.memory.summary:
            sections.append(f"[SUMMARY]\n{self.memory.summary.strip()}")

        if hasattr(self.memory, "facts") and self.memory.facts:
            facts_section = "[KNOWN FACTS]\n" + "\n".join(
                f"- {k}: {v}" for k, v in self.memory.facts.items()
            )
            sections.append(facts_section)

        conversation_section = "[RECENT CONVERSATION]\n" + "\n".join(self.memory.memory)
        sections.append(conversation_section)

        # Add lore before prompt
        if before_prompt_lore:
            sections.append(f"[LORE BEFORE PROMPT]\n" + "\n".join(before_prompt_lore))

        # Add personality
        sections.append(f"[PERSONALITY]\n{self.vtuber_personality.strip()}")

        full_prompt = "\n\n".join(sections) + f"\n\n{AI_NAME}:"
        logger.debug(f"Prompt built successfully with {len(sections)} sections.")
        return full_prompt

    def get_response(self, user_message: str) -> str:
        """
        Handles the full cycle of receiving a user message and generating an AI response.
        """
        try:
            logger.info(f'{AI_NAME} is thinking...')
            self.add_user_message(user_message)

            prompt = self.build_prompt(user_message)
            response = self.response_fn(prompt, process_text_for_speech)

            self.add_ai_message(response)
            return response

        except Exception as e:
            logger.exception(f"Error generating response: {e}")
            return "I'm sorry, I encountered an issue while processing your request. Please try again."

    def extract_keywords(self, message: str) -> list[str]:
        """
        Extract keywords from the user message based on the lorebook keys.
        """
        keywords = []
        for key in self.keywords:
            if key.lower() in message.lower():
                keywords.append(key)
        return keywords