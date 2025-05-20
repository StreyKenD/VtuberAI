import sys
import logging
from vtuber_ai.services.console_app import ConsoleApp

# =====================
# Imports (modularized)
# =====================
from vtuber_ai.core.config import load_config

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
    main()
