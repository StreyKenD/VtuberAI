import threading
import sys

# =====================
# Imports (modularized)
# =====================
from vtuber_ai.core.config import load_config
from vtuber_ai.core.response_gen import generate_response
from vtuber_ai.utils.file_ops import log_chat
from vtuber_ai.utils.text import clean_text

# =====================
# Config/Globals
# =====================
config = load_config()
TTS_MODEL = config["TTS_MODEL"]
FEMALE_VOICES = config["FEMALE_VOICES"]
EMOTION_MODEL = config["EMOTION_MODEL"]
VOICE_STYLE_DEFAULTS = config["VOICE_STYLE_DEFAULTS"]
MAX_MEMORY_LENGTH = config["MAX_MEMORY_LENGTH"]
RESPONSE_BUFFER_THRESHOLD = config["RESPONSE_BUFFER_THRESHOLD"]

conversation_memory = []
conversation_lock = threading.Lock()

# =====================
# Main VTuber Flow
# =====================
def vtuber_response(question: str) -> str:
    global conversation_memory
    with conversation_lock:
        conversation_memory.append(f"User: {question}")
        conversation_memory = conversation_memory[-MAX_MEMORY_LENGTH:]
        prompt = config["VTUBER_PERSONALITY"] + "\n" + "\n".join(conversation_memory) + "\nAiri:"
    print("\033[95mAiri is thinking...\033[0m")
    response = generate_response(prompt, clean_text)
    with conversation_lock:
        conversation_memory.append(f"Airi: {response}")
    return response

# =====================
# User Prompt
# =====================
def user_prompt() -> str:
    return input("\033[94mYou: \033[0m")

# =====================
# App Lifecycle
# =====================
def main() -> None:
    start()

def start() -> None:
    print("\033[93m✨ VTuber Airi is online! Ask anything (type 'exit' to quit).\033[0m")
    try:
        while True:
            pergunta = user_prompt()
            if pergunta.strip().lower() in {"exit", "quit"}:
                print("\033[93mAiri: Teehee~ See you later, senpai!\033[0m")
                break
            response = vtuber_response(pergunta)
            log_chat(pergunta, response)
            print("\033[93mAiri:\033[0m", response)
    except KeyboardInterrupt:
        print("\n\033[0m[INFO] Exiting due to keyboard interrupt...\033[0m")
        exit_program()

def exit_program() -> None:
    sys.exit(0)

# =====================
# Entry Point
# =====================
if __name__ == "__main__":
    main()
