import subprocess
import sys
import time
import logging
import requests
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

ollama_process = None
ollama_started_by_app = False

def start_ollama():
    """Start Ollama server and ensure Mistral model is pulled and API is ready. Returns process if started."""
    global ollama_process, ollama_started_by_app
    try:
        # Check if Ollama server is running (Windows: check for ollama.exe)
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'ollama.exe' not in result.stdout:
            print('[INFO] Pulling Mistral model for Ollama (if not present)...')
            try:
                subprocess.run(['ollama', 'pull', 'mistral'], check=True)
            except Exception as e:
                print(f'[WARN] Could not pull Mistral model: {e}')
            print('[INFO] Starting Ollama server...')
            ollama_process = subprocess.Popen(['ollama', 'serve'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            ollama_started_by_app = True
            # Wait for Ollama API to be ready
            for _ in range(30):  # Wait up to 30 seconds
                try:
                    r = requests.get('http://localhost:11434/api/tags', timeout=2)
                    if r.status_code == 200:
                        print('[INFO] Ollama API is ready.')
                        break
                except Exception:
                    pass
                time.sleep(1)
            else:
                print('[WARN] Ollama API did not become ready in time.')
        else:
            print('[INFO] Ollama is already running.')
            ollama_started_by_app = False
    except Exception as e:
        print(f'[WARN] Could not check/start Ollama: {e}')
        ollama_started_by_app = False

def stop_ollama():
    """Stop Ollama if it was started by this app."""
    global ollama_process, ollama_started_by_app
    if ollama_started_by_app and ollama_process is not None:
        print('[INFO] Stopping Ollama...')
        try:
            ollama_process.terminate()
            ollama_process.wait(timeout=10)
            print('[INFO] Ollama stopped.')
        except Exception as e:
            print(f'[WARN] Could not stop Ollama: {e}')

# =====================
# Entry Point
# =====================
if __name__ == "__main__":
    try:
        start_ollama()
        main()
    finally:
        stop_ollama()
