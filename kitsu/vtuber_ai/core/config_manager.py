import json
import threading
import time
from pathlib import Path
from typing import Any

# Set your config path here (edit if needed)
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.json"

_config_data: dict[str, Any] = {}
_config_lock = threading.Lock()

def _load_config_file() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[CONFIG LOAD ERROR] {e}")
        return {}

def _watch_config_file(interval=2):
    last_content = None
    while True:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                if content != last_content:
                    data = json.loads(content)
                    with _config_lock:
                        _config_data.clear()
                        _config_data.update(data)
                        print("[✓] Config reloaded.")
                    last_content = content
        except Exception as e:
            print(f"[CONFIG WATCH ERROR] {e}")
        time.sleep(interval)

def start_config_watcher():
    t = threading.Thread(target=_watch_config_file, daemon=True)
    t.start()

class Config:
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        with _config_lock:
            return _config_data.get(key, default)

    # Direct accessors for important configs:
    @staticmethod
    def emoji_map() -> dict:
        return Config.get("emoji_speech_map", {})

    @staticmethod
    def phonetic_overrides() -> dict:
        return Config.get("PHONETIC_OVERRIDES", {})

    @staticmethod
    def commom_actions() -> dict:
        # For typo compatibility with config.json
        return Config.get("COMMOM_ACTIONS", {})

    @staticmethod
    def streamer_name() -> str:
        return Config.get("STREAMER_NAME", "Airi")

    @staticmethod
    def max_memory_length() -> int:
        return Config.get("MAX_MEMORY_LENGTH", 6)

    @staticmethod
    def personality_prompt() -> str:
        return Config.get("VTUBER_PERSONALITY", "")

    @staticmethod
    def tts_model() -> str:
        return Config.get("TTS_MODEL", "")

    @staticmethod
    def female_voices() -> list:
        return Config.get("FEMALE_VOICES", [])

    @staticmethod
    def emotion_model() -> str:
        return Config.get("EMOTION_MODEL", "")

    @staticmethod
    def voice_style_defaults() -> dict:
        return Config.get("VOICE_STYLE_DEFAULTS", {})

    @staticmethod
    def response_buffer_threshold() -> int:
        return Config.get("RESPONSE_BUFFER_THRESHOLD", 150)

    @staticmethod
    def arpabet_map() -> dict:
        return Config.get("ARPABET_MAP", {})

    @staticmethod
    def get_all() -> dict:
        with _config_lock:
            return dict(_config_data)
