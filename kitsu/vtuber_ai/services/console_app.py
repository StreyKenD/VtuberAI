import logging
from ..utils.file_ops import log_chat
from ..utils.text import clean_text
from .conversation_service import ConversationService
from typing import List

def user_prompt() -> str:
    return input("\033[94mYou: \033[0m")

def vtuber_response(conversation_service: ConversationService, question: str) -> str:
    logging.info('Airi is thinking...')
    response = conversation_service.get_response(question)
    return response

class ConsoleApp:
    def __init__(self):
        self.history: List[str] = []
        self.conversation_service = ConversationService()

    def run(self):
        print("\033[93m✨ VTuber Airi is online! Ask anything (type 'exit' to quit, '/help' for commands).\033[0m")
        try:
            while True:
                pergunta = user_prompt()
                if not pergunta.strip():
                    print("\033[91m[WARN] Please enter a message.\033[0m")
                    continue
                cmd = pergunta.strip().lower()
                if cmd in {"exit", "quit"}:
                    print("\033[93mAiri: Teehee~ See you later, senpai!\033[0m")
                    break
                elif cmd == "/help":
                    print("\033[96mAvailable commands:\n  /help - Show this help message\n  /clear - Clear conversation history\n  /history - Show conversation history\n  exit or quit - Exit the program\033[0m")
                    continue
                elif cmd == "/clear":
                    self.conversation_service.conversation_memory.clear()
                    self.history.clear()
                    print("\033[92m[INFO] Conversation history cleared.\033[0m")
                    continue
                elif cmd == "/history":
                    if not self.history:
                        print("\033[92m[INFO] No conversation history yet.\033[0m")
                    else:
                        print("\033[92m--- Conversation History ---\033[0m")
                        for line in self.history:
                            print(line)
                        print("\033[92m---------------------------\033[0m")
                    continue
                try:
                    response = vtuber_response(self.conversation_service, pergunta)
                    log_chat(pergunta, response)
                    print("\033[93mAiri:\033[0m", response)
                    self.history.append(f"You: {pergunta}")
                    self.history.append(f"Airi: {response}")
                except Exception as e:
                    logging.error(f"Error during response generation: {e}")
                    print("\033[91m[ERROR] Something went wrong. Please try again.\033[0m")
        except KeyboardInterrupt:
            print("\n\033[0m[INFO] Exiting due to keyboard interrupt...\033[0m")
            import sys
            sys.exit(0)
