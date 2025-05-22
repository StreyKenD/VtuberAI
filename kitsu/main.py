import sys
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
root_logger = logging.getLogger(__name__)
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)

from vtuber_ai.services.console_app import ConsoleApp

# =====================
# App Lifecycle
# =====================
def main() -> None:
    app = ConsoleApp()
    root_logger.info("\033[93m✨ VTuber Airi is online! Ask anything (type 'exit' to quit, '/help' for commands).\033[0m")
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
