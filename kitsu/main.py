import sys

from ai.memory_module import ConversationMemory
from ai.tts_module import get_tts
from vtuber_ai.services.console_app import ConsoleApp
from vtuber_ai.services.ollama_manager import start_ollama, get_ollama_exit_code
import logging
from colorlog import ColoredFormatter

# Clear all existing logging handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Create colored formatter
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
)

# Set up handler with formatter
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

# Attach to root logger
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)

from vtuber_ai.services.console_app import ConsoleApp

# =====================
# App Lifecycle
# =====================
memory = None

def main() -> None:
    
    global tts, memory

    tts = get_tts()
    start_ollama()

    app = ConsoleApp()
    memory = app.conversation_service.memory
    root_logger.info("\033[93m✨ VTuber Airi is online! Ask anything (type 'exit' to quit, '/help' for commands).\033[0m")
    app.run()

def save_facts_on_exit():
    if memory is not None:
        memory.save_facts()
        root_logger.info("[INFO] Facts saved on exit.")

def exit_program() -> None:
    save_facts_on_exit()
    sys.exit(0)

# =====================
# Entry Point
# =====================
if __name__ == "__main__":
    import cProfile
    import pstats
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        main()
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(30)
        get_ollama_exit_code()
