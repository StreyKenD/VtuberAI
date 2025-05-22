import logging
from ..utils.file_ops import log_chat
from ..utils.text import clean_text
from .conversation_service import ConversationService

logger = logging.getLogger(__name__)

def user_prompt() -> str:
    return input("\033[94mYou: \033[0m")

class ConsoleApp:
    def __init__(self):
        self.conversation_service = ConversationService()

    def run(self):
        try:
            while True:
                pergunta = user_prompt()
                if not pergunta.strip():
                    logger.info("\033[91m[WARN] Please enter a message.\033[0m")
                    continue
                cmd = pergunta.strip().lower()
                if cmd in {"exit", "quit"}:
                    logger.info("\033[93mAiri: Teehee~ See you later, senpai!\033[0m")
                    break
                elif cmd == "/help":
                    logger.info("\033[96mAvailable commands:\n  /help - Show this help message\n  /clear - Clear conversation history\n  /history - Show conversation history\n  exit or quit - Exit the program\033[0m")
                    continue
                elif cmd == "/clear":
                    self.conversation_service.memory.memory.clear()
                    logger.info("\033[92m[INFO] Conversation history cleared.\033[0m")
                    continue
                elif cmd == "/history":
                    if not self.conversation_service.memory.memory:
                        logger.info("\033[92m[INFO] No conversation history yet.\033[0m")
                    else:
                        logger.info("\033[92m--- Conversation History ---\033[0m")
                        for line in self.conversation_service.memory.memory:
                            logger.info(line)
                        logger.info("\033[92m---------------------------\033[0m")
                    continue
                try:
                    response = ConversationService.get_response(self.conversation_service, pergunta)
                    log_chat(pergunta, response)
                    logger.info("\033[93mAiri:\033[0m", response)
                    self.conversation_service.memory.memory.append(f"You: {pergunta}")
                    self.conversation_service.memory.memory.append(f"Airi: {response}")
                except Exception as e:
                    logger.error(f"Error during response generation: {e}")
                    logger.info("\033[91m[ERROR] Something went wrong. Please try again.\033[0m")
        except KeyboardInterrupt:
            logger.info("\n\033[0m[INFO] Exiting due to keyboard interrupt...\033[0m")
            import sys
            sys.exit(0)
