import subprocess
import sys
import time
import logging
import requests
from vtuber_ai.services.console_app import ConsoleApp
from vtuber_ai.services.ollama_manager import start_ollama, get_ollama_exit_code

# =====================
# Imports (modularized)
# =====================
from vtuber_ai.core.config_manager import Config

# =====================
# Config/Globals
# =====================
config = Config()
EMOTION_MODEL = config.emoji_map()

MAX_MEMORY_LENGTH = config.max_memory_length()

# =====================
# Logging Setup
# =====================
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# =====================
# Service Initialization
# =====================
# Removed ConversationService initialization as it's now handled within ConsoleApp

# =====================
# App Lifecycle
# =====================
def main() -> None:
    app = ConsoleApp()
    app.run()

def exit_program() -> None:
    sys.exit(0)

# =====================
# Entry Point
# =====================
if __name__ == "__main__":
    try:
        start_ollama()
        main()
    finally:
        get_ollama_exit_code()
