import json
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Correct path to config.json in kitsu/config/config.json
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.json"))
_config_data = {}

def load_config():
    global _config_data
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config_data = json.load(f)
            print("[Config] Reloaded config.json")
    except Exception as e:
        print(f"[Config] Failed to load config: {e}")

load_config()

# Watchdog event handler
class ConfigChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if str(event.src_path).endswith("config.json"):
            load_config()

# Start the watchdog observer
def start_config_watcher():
    observer = Observer()
    observer.schedule(ConfigChangeHandler(), path=os.path.dirname(CONFIG_PATH), recursive=False)
    observer.daemon = True
    observer.start()

# Start watcher in background
threading.Thread(target=start_config_watcher, daemon=True).start()

# Accessors
def get_config():
    return _config_data

def get_voice_styles():
    return _config_data.get("voice_styles", {})

def get_emoji_map():
    return _config_data.get("emoji_speech_map", {})

def get_phonetic_overrides():
    return _config_data.get("phonetic_overrides", {})

def get_common_actions():
    return _config_data.get("common_actions", {})

def get_arpabet_map():
    return _config_data.get("arpabet_map", {})
